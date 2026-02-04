from sqlalchemy.orm import Session

from app.models.receipt_file import ReceiptFile


def get_receipt_file_for_receipt(db: Session, receipt_id, user_id) -> ReceiptFile | None:
    return (
        db.query(ReceiptFile)
        .filter(ReceiptFile.receipt_id == receipt_id, ReceiptFile.user_id == user_id)
        .order_by(ReceiptFile.created_at.desc())
        .first()
    )
