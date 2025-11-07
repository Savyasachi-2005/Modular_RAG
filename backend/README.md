# Modular RAG MVP Backend

This is the FastAPI backend scaffold per MVP_Modular_RAG.md.

## Quickstart

1. Create and activate venv with uv, install deps:

```bash
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

2. Create a `.env` at repo root (optional), e.g.:

```env
ENVIRONMENT=development
GENERATOR_PROVIDER=openai
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

3. Run server:

```bash
uvicorn backend.app.main:app --reload
```

## Configuration
Centralized in `backend/app/core/config.py`. All settings are env-driven and safe defaults are provided. See `.env` example above.

## Structure
- `backend/app/main.py` – app factory and router mounts
- `backend/app/core/` – settings and dependency wiring
- `backend/app/routers/` – HTTP APIs (ingestion, rag, admin)
- Additional modules (ingestion, index, rag, generation, plugins, orchestrator, telemetry) are added incrementally.


