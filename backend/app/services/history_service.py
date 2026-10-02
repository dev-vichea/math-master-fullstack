"""
History service providing business logic for tracking solved math problems.
Supports both dependency-injected usage in route handlers and standalone calls.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker, get_session
from app.models.db_models import SolveHistory
from app.models.schemas import SolveData
from app.repositories.history_repository import HistoryRepository


class HistoryService:
    """Service layer managing history entries."""

    def __init__(self, repository: HistoryRepository) -> None:
        self.repository = repository

    async def save_entry(self, question: str, data: SolveData) -> SolveHistory:
        """Saves a solved question to history."""
        steps_json = [step.model_dump() for step in data.steps] if data.steps else []
        return await self.repository.create(
            question=question,
            problem_type=data.problem_type,
            normalized_expression=data.normalized_expression,
            answer=data.answer,
            is_verified=data.is_verified,
            steps_json=steps_json,
        )

    async def list_entries(
        self,
        limit: int = 50,
        offset: int = 0,
        problem_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search_query: str | None = None,
    ) -> tuple[list[SolveHistory], int]:
        """Lists entries with pagination and filter criteria."""
        return await self.repository.list_paginated(
            limit=limit,
            offset=offset,
            problem_type=problem_type,
            date_from=date_from,
            date_to=date_to,
            search_query=search_query,
        )

    async def get_stats(self) -> dict[str, Any]:
        """Gets overall statistics and counts by problem type."""
        return await self.repository.get_stats()

    async def delete_entry(self, entry_id: int) -> bool:
        """Deletes a single history entry by ID."""
        return await self.repository.delete_by_id(entry_id)

    async def clear_all(self) -> int:
        """Clears all history entries."""
        return await self.repository.clear_all()


def get_history_service(
    session: AsyncSession = Depends(get_session),
) -> HistoryService:
    """FastAPI dependency for accessing HistoryService."""
    repository = HistoryRepository(session)
    return HistoryService(repository)


# ==============================================================================
# Backward Compatibility Layer
# Ensures legacy callers and tests without dependency injection continue to work
# ==============================================================================


async def save_history_entry(
    question: str,
    data: SolveData,
    session: AsyncSession | None = None,
) -> None:
    if session is not None:
        service = HistoryService(HistoryRepository(session))
        await service.save_entry(question, data)
    else:
        async with async_session_maker() as standalone_session:
            service = HistoryService(HistoryRepository(standalone_session))
            await service.save_entry(question, data)


async def list_history(
    limit: int = 50,
    offset: int = 0,
    problem_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search_query: str | None = None,
    session: AsyncSession | None = None,
) -> tuple[list[SolveHistory], int]:
    if session is not None:
        service = HistoryService(HistoryRepository(session))
        return await service.list_entries(
            limit=limit,
            offset=offset,
            problem_type=problem_type,
            date_from=date_from,
            date_to=date_to,
            search_query=search_query,
        )
    else:
        async with async_session_maker() as standalone_session:
            service = HistoryService(HistoryRepository(standalone_session))
            return await service.list_entries(
                limit=limit,
                offset=offset,
                problem_type=problem_type,
                date_from=date_from,
                date_to=date_to,
                search_query=search_query,
            )


async def get_history_stats(session: AsyncSession | None = None) -> dict[str, Any]:
    if session is not None:
        service = HistoryService(HistoryRepository(session))
        return await service.get_stats()
    else:
        async with async_session_maker() as standalone_session:
            service = HistoryService(HistoryRepository(standalone_session))
            return await service.get_stats()


async def delete_history_entry(entry_id: int, session: AsyncSession | None = None) -> bool:
    if session is not None:
        service = HistoryService(HistoryRepository(session))
        return await service.delete_entry(entry_id)
    else:
        async with async_session_maker() as standalone_session:
            service = HistoryService(HistoryRepository(standalone_session))
            return await service.delete_entry(entry_id)


async def clear_all_history(session: AsyncSession | None = None) -> int:
    if session is not None:
        service = HistoryService(HistoryRepository(session))
        return await service.clear_all()
    else:
        async with async_session_maker() as standalone_session:
            service = HistoryService(HistoryRepository(standalone_session))
            return await service.clear_all()
