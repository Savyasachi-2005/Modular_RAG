from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback

from .core.config import settings
from .ingestion.worker import worker


def create_app() -> FastAPI:
    app = FastAPI(
        title="Modular RAG MVP",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers (lazy import to avoid circular deps during settings load)
    from .routers import ingestion, search, admin

    # Import feedback router lazily to avoid import cycles
    from .routers import feedback

    app.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
    app.include_router(search.router, prefix="/rag", tags=["rag"])
    app.include_router(admin.router, tags=["admin"])  # includes /health
    app.include_router(feedback.router, tags=["feedback"])  # POST /feedback

    # Start background workers
    worker.start()

    return app


app = create_app()


