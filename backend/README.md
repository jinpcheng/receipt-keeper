# Backend scaffold

Quick start (local):

1) Copy `.env.example` to `.env` and edit `DATABASE_URL`.
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
`GET http://localhost:8000/api/v1/health`
