# Data model (Postgres)

This is a draft schema to support receipt extraction review, confirmed saves, and edits.

## Enums

- receipt_category: gas, food, office, travel, lodging, entertainment, medical, personal, other
- payment_type: credit_card, debit_card, cash, transfer, mobile_pay, other
- card_type: visa, mastercard, amex, discover, other, unknown
- receipt_status: draft, confirmed
- extraction_status: pending, completed, failed

## Tables

### users
- id (uuid, pk)
- email (text, unique, not null)
- password_hash (text, not null)
- created_at (timestamptz, not null)
- updated_at (timestamptz, not null)
- last_login_at (timestamptz, null)

### receipts
- id (uuid, pk)
- user_id (uuid, fk -> users.id, not null)
- vendor_name (text, null)
- location (text, null)
- purchased_at (timestamptz, null)
- category (receipt_category, null)
- subtotal (numeric(12,2), null)
- tax (numeric(12,2), null)
- total (numeric(12,2), null)
- currency (char(3), not null, default "CAD")
- payment_type (payment_type, null)
- card_type (card_type, null)
- card_last4 (char(4), null)
- ref_number (text, null)
- invoice_number (text, null)
- auth_number (text, null)
- notes (text, null)
- status (receipt_status, not null, default "confirmed")
- source_extraction_id (uuid, fk -> receipt_extractions.id, null)
- created_at (timestamptz, not null)
- updated_at (timestamptz, not null)

Indexes:
- receipts(user_id, purchased_at)
- receipts(user_id, category)
- receipts(user_id, total)

### receipt_files
- id (uuid, pk)
- user_id (uuid, fk -> users.id, not null)
- receipt_id (uuid, fk -> receipts.id, null) -- null until confirmed
- file_path (text, not null)
- file_name (text, not null)
- mime_type (text, not null)
- size_bytes (bigint, not null)
- sha256 (char(64), not null)
- created_at (timestamptz, not null)

Indexes:
- receipt_files(user_id, receipt_id)
- receipt_files(sha256)

### receipt_extractions
- id (uuid, pk)
- user_id (uuid, fk -> users.id, not null)
- receipt_file_id (uuid, fk -> receipt_files.id, not null)
- status (extraction_status, not null, default "pending")
- raw_ocr_text (text, null)
- extracted_json (jsonb, null) -- LLM structured output
- confidence (numeric(5,2), null)
- model_name (text, not null)
- created_at (timestamptz, not null)

Indexes:
- receipt_extractions(user_id, created_at)
- receipt_extractions(receipt_file_id)
