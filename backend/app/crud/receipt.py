import uuid

from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.models.receipt_file import ReceiptFile


def create_receipt(
    db: Session,
    user_id: uuid.UUID,
    data: dict,
) -> Receipt:
    receipt = Receipt(user_id=user_id, **data)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def update_receipt(db: Session, receipt: Receipt, data: dict) -> Receipt:
    for key, value in data.items():
        setattr(receipt, key, value)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipt_by_id(db: Session, receipt_id: uuid.UUID, user_id: uuid.UUID) -> Receipt | None:
    return db.query(Receipt).filter(Receipt.id == receipt_id, Receipt.user_id == user_id).first()


def attach_file_to_receipt(db: Session, receipt_file_id: uuid.UUID, receipt_id: uuid.UUID) -> None:
    db.query(ReceiptFile).filter(ReceiptFile.id == receipt_file_id).update({"receipt_id": receipt_id})
    db.commit()
