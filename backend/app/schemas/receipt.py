from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReceiptFields(BaseModel):
    vendor_name: Optional[str] = None
    location: Optional[str] = None
    purchased_at: Optional[datetime] = None
    category: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    payment_type: Optional[str] = None
    card_type: Optional[str] = None
    card_last4: Optional[str] = None
    ref_number: Optional[str] = None
    invoice_number: Optional[str] = None
    auth_number: Optional[str] = None
    notes: Optional[str] = None


class ReceiptCreate(ReceiptFields):
    receipt_file_id: str
    source_extraction_id: Optional[str] = None


class ReceiptUpdate(ReceiptFields):
    pass


class ReceiptRead(ReceiptFields):
    id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceiptExtractionResponse(BaseModel):
    extraction_id: str
    receipt_file_id: str
    status: str
    extracted: ReceiptFields
    confidence: Optional[float] = None
    model_name: str
    ocr_text: Optional[str] = None
