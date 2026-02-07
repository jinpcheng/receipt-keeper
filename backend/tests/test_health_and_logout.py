import httpx
import pytest


def _client(app) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_ok(app):
    async with _client(app) as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_logout_ok(app):
    async with _client(app) as client:
        # endpoint ignores payload; keep it minimal but valid shape
        res = await client.post("/api/v1/auth/logout", json={"refresh_token": "x"})
        assert res.status_code == 200
        assert res.json() == {"ok": True}

