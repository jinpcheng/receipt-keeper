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

Migrations:

```bash
alembic -c alembic.ini upgrade head
```

Docker Compose (recommended for local dev):

```bash
docker compose up -d
docker compose exec api alembic -c alembic.ini upgrade head
```
