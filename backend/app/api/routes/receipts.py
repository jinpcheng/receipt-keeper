import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.crud.receipt import attach_file_to_receipt, create_receipt, get_receipt_by_id, update_receipt
from app.models.enums import ExtractionStatus
from app.models.receipt_extraction import ReceiptExtraction
from app.models.receipt_file import ReceiptFile
from app.models.user import User
from app.db.session import get_db
from app.schemas.receipt import ReceiptCreate, ReceiptExtractionResponse, ReceiptFields, ReceiptRead, ReceiptUpdate
from app.services.extraction import extract_receipt


router = APIRouter(prefix="/receipts")


@router.post("/extractions", response_model=ReceiptExtractionResponse, status_code=status.HTTP_201_CREATED)
def create_extraction(
    file: UploadFile = File(...),
    currency: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name missing")

    extension = Path(file.filename).suffix[:10]
    file_id = uuid.uuid4()
    storage_root = Path(settings.storage_dir) / str(current_user.id)
    storage_root.mkdir(parents=True, exist_ok=True)
    file_name = f"{file_id}{extension}"
    file_path = storage_root / file_name

    sha256 = hashlib.sha256()
    size_bytes = 0
    try:
        with file_path.open("wb") as handle:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                sha256.update(chunk)
                size_bytes += len(chunk)
    finally:
        file.file.close()

    receipt_file = ReceiptFile(
        id=file_id,
        user_id=current_user.id,
        receipt_id=None,
        file_path=str(file_path),
        file_name=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        sha256=sha256.hexdigest(),
    )
    db.add(receipt_file)
    db.commit()
    db.refresh(receipt_file)

    extraction = ReceiptExtraction(
        user_id=current_user.id,
        receipt_file_id=receipt_file.id,
        status=ExtractionStatus.pending,
        raw_ocr_text=None,
        extracted_json=None,
        confidence=None,
        model_name=settings.ollama_model,
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    try:
        result = extract_receipt(str(file_path), currency)
    except Exception:
        extraction.status = ExtractionStatus.failed
        db.add(extraction)
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Extraction failed")

    extracted_fields = ReceiptFields.model_validate(result.extracted)
    if currency and not extracted_fields.currency:
        extracted_fields.currency = currency

    extraction.status = ExtractionStatus.completed
    extraction.raw_ocr_text = result.ocr_text
    extraction.extracted_json = extracted_fields.model_dump()
    extraction.confidence = result.confidence
    extraction.model_name = result.model_name
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    return ReceiptExtractionResponse(
        extraction_id=str(extraction.id),
        receipt_file_id=str(receipt_file.id),
        status=extraction.status.value,
        extracted=extracted_fields,
        confidence=float(extraction.confidence) if extraction.confidence is not None else None,
        model_name=extraction.model_name,
        ocr_text=extraction.raw_ocr_text,
    )


@router.post("", response_model=ReceiptRead, status_code=status.HTTP_201_CREATED)
def create_receipt_record(
    payload: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude={"receipt_file_id"})
    receipt = create_receipt(db, user_id=current_user.id, data=data)
    attach_file_to_receipt(db, uuid.UUID(payload.receipt_file_id), receipt.id)
    return ReceiptRead.model_validate(receipt)


@router.patch("/{receipt_id}", response_model=ReceiptRead)
def update_receipt_record(
    receipt_id: uuid.UUID,
    payload: ReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = get_receipt_by_id(db, receipt_id=receipt_id, user_id=current_user.id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")

    data = payload.model_dump(exclude_unset=True)
    receipt = update_receipt(db, receipt, data)
    return ReceiptRead.model_validate(receipt)
