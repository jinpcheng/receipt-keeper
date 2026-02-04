"""Initial schema

Revision ID: 20260204_0001
Revises: 
Create Date: 2026-02-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260204_0001"
down_revision = None
branch_labels = None
depends_on = None


receipt_category = sa.Enum(
    "gas",
    "food",
    "office",
    "travel",
    "lodging",
    "entertainment",
    "medical",
    "personal",
    "other",
    name="receipt_category",
)
payment_type = sa.Enum(
    "credit_card",
    "debit_card",
    "cash",
    "transfer",
    "mobile_pay",
    "other",
    name="payment_type",
)
card_type = sa.Enum(
    "visa",
    "mastercard",
    "amex",
    "discover",
    "other",
    "unknown",
    name="card_type",
)
receipt_status = sa.Enum("draft", "confirmed", name="receipt_status")
extraction_status = sa.Enum("pending", "completed", "failed", name="extraction_status")


def upgrade() -> None:
    bind = op.get_bind()
    receipt_category.create(bind, checkfirst=True)
    payment_type.create(bind, checkfirst=True)
    card_type.create(bind, checkfirst=True)
    receipt_status.create(bind, checkfirst=True)
    extraction_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "receipt_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "receipt_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("receipt_file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("receipt_files.id"), nullable=False),
        sa.Column("status", extraction_status, server_default="pending", nullable=False),
        sa.Column("raw_ocr_text", sa.Text(), nullable=True),
        sa.Column("extracted_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("vendor_name", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("purchased_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("category", receipt_category, nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax", sa.Numeric(12, 2), nullable=True),
        sa.Column("total", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), server_default="CAD", nullable=False),
        sa.Column("payment_type", payment_type, nullable=True),
        sa.Column("card_type", card_type, nullable=True),
        sa.Column("card_last4", sa.String(length=4), nullable=True),
        sa.Column("ref_number", sa.Text(), nullable=True),
        sa.Column("invoice_number", sa.Text(), nullable=True),
        sa.Column("auth_number", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", receipt_status, server_default="confirmed", nullable=False),
        sa.Column(
            "source_extraction_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_receipts_user_purchased_at", "receipts", ["user_id", "purchased_at"])
    op.create_index("ix_receipts_user_category", "receipts", ["user_id", "category"])
    op.create_index("ix_receipts_user_total", "receipts", ["user_id", "total"])
    op.create_index("ix_receipt_files_user_receipt", "receipt_files", ["user_id", "receipt_id"])
    op.create_index("ix_receipt_files_sha256", "receipt_files", ["sha256"])
    op.create_index("ix_receipt_extractions_user_created_at", "receipt_extractions", ["user_id", "created_at"])
    op.create_index("ix_receipt_extractions_receipt_file_id", "receipt_extractions", ["receipt_file_id"])

    op.create_foreign_key(
        "fk_receipt_files_receipt_id",
        "receipt_files",
        "receipts",
        ["receipt_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_receipts_source_extraction_id",
        "receipts",
        "receipt_extractions",
        ["source_extraction_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_index("ix_receipt_extractions_receipt_file_id", table_name="receipt_extractions")
    op.drop_index("ix_receipt_extractions_user_created_at", table_name="receipt_extractions")
    op.drop_index("ix_receipt_files_sha256", table_name="receipt_files")
    op.drop_index("ix_receipt_files_user_receipt", table_name="receipt_files")
    op.drop_index("ix_receipts_user_total", table_name="receipts")
    op.drop_index("ix_receipts_user_category", table_name="receipts")
    op.drop_index("ix_receipts_user_purchased_at", table_name="receipts")
    op.drop_constraint("fk_receipts_source_extraction_id", "receipts", type_="foreignkey")
    op.drop_constraint("fk_receipt_files_receipt_id", "receipt_files", type_="foreignkey")
    op.drop_table("receipts")
    op.drop_table("receipt_extractions")
    op.drop_table("receipt_files")
    op.drop_table("users")

    bind = op.get_bind()
    extraction_status.drop(bind, checkfirst=True)
    receipt_status.drop(bind, checkfirst=True)
    card_type.drop(bind, checkfirst=True)
    payment_type.drop(bind, checkfirst=True)
    receipt_category.drop(bind, checkfirst=True)
