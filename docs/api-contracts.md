# API contracts (draft)

Base path: /api/v1
Auth: JWT in Authorization: Bearer <token>

## Auth

POST /auth/register
- body: { email, password }
- response: { access_token, refresh_token, user }

POST /auth/login
- body: { email, password }
- response: { access_token, refresh_token, user }

POST /auth/refresh
- body: { refresh_token }
- response: { access_token }

POST /auth/logout
- body: { refresh_token }

## Receipt extraction (review before save)

POST /receipts/extractions
- content-type: multipart/form-data
- fields: file, file_name (optional), currency (optional)
- response: {
    extraction_id,
    receipt_file_id,
    extracted: { ...receipt_fields },
    confidence,
    model_name,
    ocr_text
  }

Client flow:
1) Upload image to /receipts/extractions
2) Show extracted data to user for confirmation/edit
3) Save confirmed receipt using POST /receipts

## Receipts

POST /receipts
- body: {
    source_extraction_id (optional),
    receipt_file_id,
    ...receipt_fields
  }
- response: { receipt }

GET /receipts
- query filters: start_date, end_date, category, min_total, max_total, payment_type, vendor
- response: { items, page, page_size, total }

GET /receipts/{id}
- response: { receipt }

PATCH /receipts/{id}
- body: { ...receipt_fields }
- response: { receipt }

DELETE /receipts/{id} (optional)
- response: { ok: true }

GET /receipts/{id}/files
- response: { files }

GET /receipts/{id}/photo
- response: image bytes

GET /receipts/export
- query filters: same as GET /receipts, format=csv
- response: text/csv

## Receipt fields (shared)

receipt_fields:
- vendor_name
- location
- purchased_at (ISO 8601)
- category
- subtotal
- tax
- total
- currency
- payment_type
- card_type
- card_last4
- ref_number
- invoice_number
- auth_number
- notes
