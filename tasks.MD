# Tasks

Build an Android app and a PC backend to manage receipts on the same WiFi network.

## Decisions

- Database: Postgres
- Backend language: Python (FastAPI)
- AI stack: local OCR + local LLM (PaddleOCR + Ollama)

## Receipt data fields

- Vendor name
- Location
- Date/time
- Category (gas, food, office, etc.)
- Subtotal
- Tax (HST, GST, etc.)
- Total
- Payment type (credit card, cash, etc.)
- Credit card type (Visa, Mastercard)
- Credit card # (last 4 digits)
- Ref#
- Invoice #
- Auth#

## Devices and network

- Android phone
- Windows 11 Pro desktop PC (Docker + WSL 2 installed, 64GB RAM, GeForce 3060Ti)
- Both devices are on the same WiFi network

## Architecture

Android app (client):

- Register/login user
- Take receipt photo with camera
- Upload photo to PC storage
- Call PC AI service to extract receipt data from photo
- Show extracted data for user confirmation, then save receipt record
- Query receipts by date range, category, amount range, payment type
- Edit/modify saved receipt data
- Export receipts to CSV

PC backend (service):

- Receipt keeper API exposed to LAN (JWT auth)
- Local AI pipeline for receipt extraction (PaddleOCR + Ollama)
- File storage for receipt photos
- Postgres database with CRUD (including update/edit) + query filters + CSV export
- Encrypted network traffic (HTTPS on LAN)

## Implementation plan

0) Ensure GitHub repo is created and initialized.
1) Define API contracts and data model (users, receipts, files, enums).
2) Backend scaffold (FastAPI + Postgres + JWT + storage).
3) AI pipeline (OCR -> LLM structured extraction -> validation).
4) Android app scaffold (auth, camera capture, upload, review/confirm, list/search, detail/edit).
5) Deployment (Docker Compose: API + Postgres + Ollama).
6) QA (E2E flow, OCR accuracy tests, security tests, CSV export validation).

## Status (2026-02-07)

- [x] Repo initialized.
- [x] Backend scaffold: FastAPI + Postgres + JWT + storage.
- [x] Android scaffold: auth + capture + upload + review/edit + list/search.
- [x] Deployment: Docker Compose (API + Postgres + Ollama).
- [x] Backend unit tests: enforced at 100% line coverage.
- [x] Android: runtime-configurable API base URL (Settings screen).
- [ ] Encrypted network traffic (HTTPS on LAN): implemented compose overlay (Caddy), needs device verification.
- [ ] QA: run the full flow on a physical phone over WiFi and validate CSV export and OCR accuracy.
