import io
import uuid
from datetime import timedelta
from pathlib import Path

import httpx
import pytest

from app.core.security import create_token, get_access_token
from app.models.enums import ExtractionStatus
from app.models.receipt_extraction import ReceiptExtraction
from app.models.receipt_file import ReceiptFile
from app.services.extraction import ExtractionResult


def _client(app) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def _register(client: httpx.AsyncClient, email: str = "user@example.com") -> dict:
    res = await client.post("/api/v1/auth/register", json={"email": email, "password": "ChangeMe123!"})
    assert res.status_code == 201, res.text
    return res.json()


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(app):
    async with _client(app) as client:
        await _register(client, email="dup@example.com")
        dup = await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "ChangeMe123!"})
        assert dup.status_code == 409


@pytest.mark.asyncio
async def test_refresh_invalid_token_returns_401(app):
    async with _client(app) as client:
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-jwt"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token_returns_400(app):
    async with _client(app) as client:
        reg = await _register(client, email="refresh-access@example.com")
        access_token = reg["access_token"]
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_refresh_missing_subject_returns_400(app):
    # craft a refresh token with missing/empty subject to hit the guard branch
    token = create_token(subject="", token_type="refresh", expires_delta=timedelta(minutes=5))
    async with _client(app) as client:
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_protected_route_requires_bearer_token(app):
    async with _client(app) as client:
        res = await client.get("/api/v1/receipts")
        # fastapi.security.HTTPBearer returns 403 when missing auth header
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_protected_route_rejects_refresh_token(app):
    async with _client(app) as client:
        reg = await _register(client, email="refresh-protected@example.com")
        refresh_token = reg["refresh_token"]
        res = await client.get("/api/v1/receipts", headers={"Authorization": f"Bearer {refresh_token}"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_subject_returns_401(app):
    token = create_token(subject="", token_type="access", expires_delta=timedelta(minutes=5))
    async with _client(app) as client:
        res = await client.get("/api/v1/receipts", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_token_format_returns_401(app):
    async with _client(app) as client:
        res = await client.get("/api/v1/receipts", headers={"Authorization": "Bearer not-a-jwt"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_user_not_found_returns_401(app):
    token = get_access_token(str(uuid.uuid4()))
    async with _client(app) as client:
        res = await client.get("/api/v1/receipts", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_extraction_missing_filename_returns_400(app):
    async with _client(app) as client:
        reg = await _register(client, email="missing-fn@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        files = {"file": ("", io.BytesIO(b"fake image data"), "image/jpeg")}
        res = await client.post("/api/v1/receipts/extractions", headers=headers, files=files)
        # httpx/starlette treat an empty filename as invalid/missing upload, so
        # request validation fails before the route runs.
        assert res.status_code == 422


def test_extraction_direct_call_missing_filename_returns_400(app, db_session):
    from io import BytesIO

    from starlette.datastructures import UploadFile

    from app.api.routes.receipts import create_extraction
    from app.models.user import User

    # Covers the explicit filename guard in the route.
    file = UploadFile(filename="", file=BytesIO(b"fake"))
    user = User(id=uuid.uuid4(), email="x@example.com", password_hash="x")

    with pytest.raises(Exception) as exc:
        create_extraction(file=file, currency=None, db=db_session, current_user=user)
    assert "File name missing" in str(exc.value)


@pytest.mark.asyncio
async def test_extraction_injects_currency_when_missing(app, monkeypatch, tmp_path):
    def fake_extract_receipt(_path: str, _currency: str | None):
        return ExtractionResult(
            ocr_text="Store\nTotal 1.23",
            extracted={"vendor_name": "No Currency", "total": 1.23},
            model_name="fake-model",
            confidence=0.9,
        )

    monkeypatch.setattr("app.services.extraction.extract_receipt", fake_extract_receipt)
    monkeypatch.setattr("app.api.routes.receipts.extract_receipt", fake_extract_receipt)
    monkeypatch.setattr("app.core.config.settings.storage_dir", str(tmp_path))

    async with _client(app) as client:
        reg = await _register(client, email="inject-currency@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        files = {"file": ("receipt.jpg", io.BytesIO(b"fake image data"), "image/jpeg")}
        res = await client.post(
            "/api/v1/receipts/extractions",
            headers=headers,
            files=files,
            data={"currency": "CAD"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["extracted"]["currency"] == "CAD"


@pytest.mark.asyncio
async def test_extraction_failure_sets_status_failed(app, monkeypatch, tmp_path, db_session):
    def failing_extract(_path: str, _currency: str | None):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.extraction.extract_receipt", failing_extract)
    monkeypatch.setattr("app.api.routes.receipts.extract_receipt", failing_extract)
    monkeypatch.setattr("app.core.config.settings.storage_dir", str(tmp_path))

    async with _client(app) as client:
        reg = await _register(client, email="extract-fail@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        files = {"file": ("receipt.jpg", io.BytesIO(b"fake image data"), "image/jpeg")}
        res = await client.post("/api/v1/receipts/extractions", headers=headers, files=files)
        assert res.status_code == 500

        # Ensure the extraction record is marked failed.
        extraction = db_session.query(ReceiptExtraction).order_by(ReceiptExtraction.created_at.desc()).first()
        assert extraction is not None
        assert extraction.status == ExtractionStatus.failed


@pytest.mark.asyncio
async def test_create_receipt_rejects_unknown_receipt_file(app):
    async with _client(app) as client:
        reg = await _register(client, email="unknown-file@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        payload = {
            "receipt_file_id": str(uuid.uuid4()),
            "vendor_name": "Should Fail",
            "total": 9.99,
            "currency": "CAD",
        }
        res = await client.post("/api/v1/receipts", headers=headers, json=payload)
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_photo_missing_returns_404(app, monkeypatch, tmp_path, db_session):
    def fake_extract_receipt(_path: str, _currency: str | None):
        return ExtractionResult(
            ocr_text="Store\nTotal 12.34",
            extracted={"vendor_name": "Sample Store", "total": 12.34, "currency": "CAD"},
            model_name="fake-model",
            confidence=0.9,
        )

    monkeypatch.setattr("app.services.extraction.extract_receipt", fake_extract_receipt)
    monkeypatch.setattr("app.api.routes.receipts.extract_receipt", fake_extract_receipt)
    monkeypatch.setattr("app.core.config.settings.storage_dir", str(tmp_path))

    async with _client(app) as client:
        reg = await _register(client, email="photo-missing@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        files = {"file": ("receipt.jpg", io.BytesIO(b"fake image data"), "image/jpeg")}
        extraction = await client.post("/api/v1/receipts/extractions", headers=headers, files=files)
        assert extraction.status_code == 201
        extraction_data = extraction.json()

        create_receipt = await client.post(
            "/api/v1/receipts",
            headers=headers,
            json={
                "receipt_file_id": extraction_data["receipt_file_id"],
                "source_extraction_id": extraction_data["extraction_id"],
                "vendor_name": "Sample Store",
                "total": 12.34,
                "currency": "CAD",
            },
        )
        assert create_receipt.status_code == 201
        receipt_id = create_receipt.json()["id"]

        receipt_file = db_session.query(ReceiptFile).filter(ReceiptFile.receipt_id == receipt_id).first()
        assert receipt_file is not None
        Path(receipt_file.file_path).unlink(missing_ok=True)

        photo = await client.get(f"/api/v1/receipts/{receipt_id}/photo", headers=headers)
        assert photo.status_code == 404


@pytest.mark.asyncio
async def test_photo_receipt_file_not_found_returns_404(app, db_session):
    # Create a user + receipt directly (no attached ReceiptFile) then hit /photo.
    from app.models.receipt import Receipt
    from app.models.user import User

    user = User(email="nofile@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    receipt = Receipt(user_id=user.id, vendor_name="NoFile")
    db_session.add(receipt)
    db_session.commit()
    db_session.refresh(receipt)

    token = get_access_token(str(user.id))
    async with _client(app) as client:
        res = await client.get(f"/api/v1/receipts/{receipt.id}/photo", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_photo_receipt_not_found_returns_404(app):
    async with _client(app) as client:
        reg = await _register(client, email="photo-404@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        missing = str(uuid.uuid4())
        res = await client.get(f"/api/v1/receipts/{missing}/photo", headers=headers)
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_receipt_not_found_returns_404(app):
    async with _client(app) as client:
        reg = await _register(client, email="update-404@example.com")
        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        receipt_id = str(uuid.uuid4())
        res = await client.patch(f"/api/v1/receipts/{receipt_id}", headers=headers, json={"notes": "x"})
        assert res.status_code == 404
