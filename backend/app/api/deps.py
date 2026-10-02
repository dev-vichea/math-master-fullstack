"""
Shared FastAPI dependency injection.

Centralizes common dependencies to avoid repetition across endpoints:
  - Database session lifecycle
  - Cached settings access
  - Service instance creation
  - Solve cache access

Usage in endpoints:
    @router.post("/solve")
    async def solve(
        request: SolveRequest,
        settings: Settings = Depends(get_settings_dep),
        db: AsyncSession = Depends(get_db_session),
    ):
        ...
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.cache import SolveCache, get_solve_cache
from app.db.session import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session that auto-closes after the request."""
    async with get_session() as session:
        yield session


def get_settings_dep() -> Settings:
    """FastAPI-compatible dependency for cached settings."""
    return get_settings()


def get_cache_dep() -> SolveCache:
    """FastAPI-compatible dependency for the solve cache."""
    return get_solve_cache()
