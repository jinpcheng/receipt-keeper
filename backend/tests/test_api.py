import io

import pytest
import httpx

from app.services.extraction import ExtractionResult


@pytest.mark.asyncio
async def test_auth_register_and_login(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "password": "ChangeMe123!"},
        )
        assert register.status_code == 201
        data = register.json()
        assert "access_token" in data
        assert "refresh_token" in data

        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "ChangeMe123!"},
        )
        assert login.status_code == 200
        data = login.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_auth_refresh_and_invalid_login(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register = await client.post(
            "/api/v1/auth/register",
            json={"email": "refresh@example.com", "password": "ChangeMe123!"},
        )
        refresh_token = register.json()["refresh_token"]

        refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh.status_code == 200
        assert "access_token" in refresh.json()

        bad_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "refresh@example.com", "password": "WrongPass"},
        )
        assert bad_login.status_code == 401


@pytest.mark.asyncio
async def test_receipt_flow(app, monkeypatch, tmp_path):
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

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        register = await client.post(
            "/api/v1/auth/register",
            json={"email": "flow@example.com", "password": "ChangeMe123!"},
        )
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        file_content = io.BytesIO(b"fake image data")
        files = {"file": ("receipt.jpg", file_content, "image/jpeg")}
        extraction = await client.post(
            "/api/v1/receipts/extractions",
            headers=headers,
            files=files,
            data={"currency": "CAD"},
        )
        assert extraction.status_code == 201
        extraction_data = extraction.json()
        receipt_file_id = extraction_data["receipt_file_id"]
        extraction_id = extraction_data["extraction_id"]

        create_receipt = await client.post(
            "/api/v1/receipts",
            headers=headers,
            json={
                "receipt_file_id": receipt_file_id,
                "source_extraction_id": extraction_id,
                "vendor_name": "Sample Store",
                "total": 12.34,
                "currency": "CAD",
            },
        )
        assert create_receipt.status_code == 201
        receipt_id = create_receipt.json()["id"]

        update_receipt = await client.patch(
            f"/api/v1/receipts/{receipt_id}",
            headers=headers,
            json={"notes": "Updated via test"},
        )
        assert update_receipt.status_code == 200

        list_receipts = await client.get("/api/v1/receipts?page=1&page_size=10", headers=headers)
        assert list_receipts.status_code == 200
        assert list_receipts.json()["total"] >= 1

        export_csv = await client.get("/api/v1/receipts/export", headers=headers)
        assert export_csv.status_code == 200
        assert export_csv.headers["content-type"].startswith("text/csv")

        photo = await client.get(f"/api/v1/receipts/{receipt_id}/photo", headers=headers)
        assert photo.status_code == 200
