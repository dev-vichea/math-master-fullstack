"""Creates tables if they don't exist yet. Called from the FastAPI lifespan
on startup. For a real migration history later, swap this for Alembic —
nothing else needs to change since the ORM models stay the same."""

import asyncio

from app.db.session import engine
from app.models.db_models import Base


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
