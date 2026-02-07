import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CardType, PaymentType, ReceiptCategory, ReceiptStatus


class Receipt(Base):
    __tablename__ = "receipts"
    __table_args__ = (
        Index("ix_receipts_user_purchased_at", "user_id", "purchased_at"),
        Index("ix_receipts_user_category", "user_id", "category"),
        Index("ix_receipts_user_total", "user_id", "total"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    category: Mapped[ReceiptCategory | None] = mapped_column(
        Enum(ReceiptCategory, name="receipt_category"),
        nullable=True,
    )
    subtotal: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    tax: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="CAD")
    payment_type: Mapped[PaymentType | None] = mapped_column(
        Enum(PaymentType, name="payment_type"),
        nullable=True,
    )
    card_type: Mapped[CardType | None] = mapped_column(
        Enum(CardType, name="card_type"),
        nullable=True,
    )
    card_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    ref_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReceiptStatus] = mapped_column(
        Enum(ReceiptStatus, name="receipt_status"),
        nullable=False,
        server_default="confirmed",
    )
    source_extraction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "receipt_extractions.id",
            name="fk_receipts_source_extraction_id",
            use_alter=True,
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="receipts")
    source_extraction = relationship("ReceiptExtraction", back_populates="receipt", uselist=False)
    files = relationship("ReceiptFile", back_populates="receipt")
