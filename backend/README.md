# Backend scaffold

Quick start (local):

1) Copy `.env.example` to `.env` and set a strong `SECRET_KEY`.
2) Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

3) Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:
`GET http://localhost:8081/api/v1/health`

Auth + extraction flow:
1) Register/Login to get `access_token`
2) `POST /api/v1/receipts/extractions` with `Authorization: Bearer <token>` and form-data `file`

Queries + export:
- `GET /api/v1/receipts` with filters: `start_date`, `end_date`, `category`, `min_total`, `max_total`, `payment_type`, `vendor`
- `GET /api/v1/receipts/export` returns CSV
- `GET /api/v1/receipts/{id}/photo` returns receipt image

Postman:

- Collection: `docs/postman/receipt-keeper.postman_collection.json`
- Environment: `docs/postman/receipt-keeper.postman_environment.json`

Tests:
1) Install dev deps:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

2) Set `TEST_DATABASE_URL` (must be Postgres, not SQLite), then:

```bash
pytest
```

Run tests via Docker Compose (uses the `db` service):

```bash
docker compose up -d
docker compose exec db psql -U receipt_user -d postgres -c "CREATE DATABASE receipt_keeper_test;"
docker compose exec api python -m pip install -r /app/requirements-dev.txt
docker compose exec -w /app -e PYTHONPATH=/app -e TEST_DATABASE_URL=postgresql+psycopg2://receipt_user:receipt_pass@db:5432/receipt_keeper_test api pytest
```

Coverage:
- Coverage reports are generated in the test output and `coverage.xml`.
- Tests fail if coverage drops below 100%.

HTTPS on LAN (optional, for phone testing):

This uses Caddy with a locally-trusted CA (`tls internal`) as a reverse proxy in front of the API.

1) Start the stack with the HTTPS overlay:

```bash
# Set this to your PC's LAN IP so the cert is valid for your phone's URL.
# PowerShell:
#   $env:CADDY_HOST="192.168.1.50"
# bash/zsh:
#   export CADDY_HOST=192.168.1.50

docker compose -f docker-compose.yml -f docker-compose.https.yml up -d
```

2) Extract Caddy's root certificate and install it on Android as a *user* CA:

```bash
docker cp receipt-keeper-caddy:/data/caddy/pki/authorities/local/root.crt ./caddy-root.crt
```

3) Verify from the phone browser:
`https://<PC-LAN-IP>:8443/api/v1/health`

4) In the Android app Settings, set base URL:
`https://<PC-LAN-IP>:8443/api/v1/`

Git hook (optional):
- Enable repo hooks: `git config core.hooksPath .githooks`
- The pre-commit hook runs backend tests when `backend/` files are staged.
- Set `TEST_DATABASE_URL` so the hook can run tests.

Migrations:

```bash
alembic -c alembic.ini upgrade head
```

Docker Compose (recommended for local dev):

```bash
docker compose up -d
docker compose exec api alembic -c alembic.ini upgrade head
```

OCR + LLM setup:
- OCR uses PaddleOCR (CPU). LLM uses Ollama.
- For local installs, Python 3.10 is recommended to avoid PyMuPDF build issues.
- Pull a model into Ollama (example):

```bash
docker compose exec ollama ollama pull llama3.1
```

- Configure `.env` if you want a different model or OCR language.
