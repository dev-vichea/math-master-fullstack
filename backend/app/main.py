"""
Application entrypoint for Khmer Math Lab API.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Interactive API documentation:
    Swagger UI: http://127.0.0.1:8000/docs
    ReDoc:      http://127.0.0.1:8000/redoc
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestCorrelationMiddleware
from app.db.init_db import init_models
from app.db.session import close_db_engine
from app.models.schemas import APIResponse

settings = get_settings()

# Initialize centralized logging
setup_logging(log_level=settings.log_level)
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and graceful shutdown."""
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"[env={settings.environment}, debug={settings.debug}]"
    )
    await init_models()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down application and closing database connections...")
    await close_db_engine()
    logger.info("Shutdown complete.")


TAGS_METADATA = [
    {
        "name": "math",
        "description": "Deterministic Khmer & English math solving and step generation.",
    },
    {
        "name": "vision",
        "description": "Multi-engine OCR and Khmer handwritten/printed math recognition.",
    },
    {
        "name": "history",
        "description": "History inspection, filtering, and query statistics.",
    },
    {
        "name": "system",
        "description": "Operational health check and monitoring endpoints.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-ready backend for Khmer Math Lab: understands Khmer and English math, "
        "solves deterministically via SymPy, provides verified step-by-step explanations, "
        "and supports multimodal vision OCR."
    ),
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Correlation ID and access logging middleware (first in pipeline)
app.add_middleware(RequestCorrelationMiddleware)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles domain and application-specific exceptions uniformly."""
    logger.warning(f"Application exception on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(success=False, data=exc.details, error=exc.message).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Safety net for unhandled exceptions, preventing raw stack traces from leaking."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            data=None,
            error="An internal server error occurred. Please try again later.",
        ).model_dump(),
    )


# API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Frontend web UI static mount if present
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists() and (frontend_dir / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "environment": settings.environment,
        }
