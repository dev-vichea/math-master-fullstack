"""
Database engine and async session factory.

Connection pool settings are tuned for production readiness:
- pool_size: Number of persistent connections (scales with workers)
- max_overflow: Extra connections allowed under load
- pool_recycle: Prevent stale connections (important for Postgres)
- pool_pre_ping: Verify connections before use

For SQLite (dev), pooling is disabled since it's file-based.
For Postgres (prod), these settings prevent connection exhaustion.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

_settings = get_settings()

# Connection pool configuration — tune per environment
_is_sqlite = "sqlite" in _settings.database_url

_engine_kwargs = {
    "echo": _settings.debug and _settings.environment == "development",
    "future": True,
}

if not _is_sqlite:
    # Postgres / production pool settings
    _engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,  # Recycle connections every 30 minutes
        "pool_pre_ping": True,  # Verify connection liveness before checkout
    })

engine = create_async_engine(_settings.database_url, **_engine_kwargs)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: `session: AsyncSession = Depends(get_session)`."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_engine() -> None:
    """Closes all database connections during application shutdown."""
    await engine.dispose()
