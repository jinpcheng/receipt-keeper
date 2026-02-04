import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.enums import ExtractionStatus
from app.models.receipt_extraction import ReceiptExtraction
from app.models.receipt_file import ReceiptFile
from app.models.user import User
from app.db.session import get_db
from app.schemas.receipt import ReceiptExtractionResponse, ReceiptFields


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

    extracted = ReceiptFields(currency=currency)
    extraction = ReceiptExtraction(
        user_id=current_user.id,
        receipt_file_id=receipt_file.id,
        status=ExtractionStatus.completed,
        raw_ocr_text="",
        extracted_json=extracted.model_dump(),
        confidence=0,
        model_name="local-ocr-llm-placeholder",
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    return ReceiptExtractionResponse(
        extraction_id=str(extraction.id),
        receipt_file_id=str(receipt_file.id),
        status=extraction.status.value,
        extracted=extracted,
        confidence=float(extraction.confidence or 0),
        model_name=extraction.model_name,
        ocr_text=extraction.raw_ocr_text,
    )
