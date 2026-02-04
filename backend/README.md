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

Coverage:
- Coverage reports are generated in the test output and `coverage.xml`.
- Tests fail if coverage drops below 80%.

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
- Pull a model into Ollama (example):

```bash
docker compose exec ollama ollama pull llama3.1
```

- Configure `.env` if you want a different model or OCR language.
