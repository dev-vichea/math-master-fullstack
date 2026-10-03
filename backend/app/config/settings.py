"""
Central application configuration.

Everything environment-specific (database URL, CORS, debug mode) lives here
so the rest of the codebase never reads os.environ directly. This is what
lets the same code run unchanged in local development, CI, and later on a
real server.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Khmer Math Lab API"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"

    # List of allowed origins or comma-separated string from .env
    cors_origins: list[str] = ["*"]

    # aiosqlite for local dev on the M3 Pro. Swap for a Postgres URL later
    # (e.g. "postgresql+asyncpg://...") without touching any other file.
    database_url: str = "sqlite+aiosqlite:///./khmer_math_lab.db"

    # Math Vision / OCR provider: "stub", "tesseract", "kiri" (khmer_ocr), "mathpix", "google", or "gemini"
    vision_provider: str = "stub"

    # Gemini API credentials (if using gemini vision provider)
    gemini_api_key: str | None = None

    # Mathpix credentials (if using mathpix provider)
    mathpix_app_id: str | None = None
    mathpix_app_key: str | None = None

    # Google Vision credentials path (if using google provider)
    google_application_credentials: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", str(Path(__file__).resolve().parent.parent.parent / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() -> os.environ parsing only happens once."""
    return Settings()
