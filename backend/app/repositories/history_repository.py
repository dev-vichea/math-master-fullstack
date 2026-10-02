"""
Repository for SolveHistory database operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_

from app.models.db_models import SolveHistory


class HistoryRepository:
    """Encapsulates data access and queries for SolveHistory entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        question: str,
        problem_type: str,
        normalized_expression: str,
        answer: str | None,
        is_verified: bool,
        steps_json: list[dict[str, Any]] | None,
    ) -> SolveHistory:
        """Creates and commits a new history entry."""
        entry = SolveHistory(
            question=question,
            problem_type=problem_type,
            normalized_expression=normalized_expression,
            answer=answer,
            is_verified=is_verified,
            steps_json=steps_json,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def list_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        problem_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search_query: str | None = None,
    ) -> tuple[list[SolveHistory], int]:
        """
        Retrieves paginated history entries along with the total count matching the criteria.
        Uses SQL aggregation for O(1) count overhead instead of in-memory list length.
        """
        conditions = []

        if problem_type:
            conditions.append(SolveHistory.problem_type == problem_type)

        if date_from:
            conditions.append(SolveHistory.created_at >= date_from)

        if date_to:
            conditions.append(SolveHistory.created_at <= date_to)

        if search_query:
            conditions.append(SolveHistory.question.ilike(f"%{search_query}%"))

        # Optimized count query
        count_query = select(func.count(SolveHistory.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one()

        # Data query with pagination
        query = select(SolveHistory).order_by(SolveHistory.id.desc())
        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        entries = list(result.scalars().all())

        return entries, total_count

    async def get_stats(self) -> dict[str, Any]:
        """
        Calculates aggregate statistics using SQL GROUP BY and COUNT.
        """
        # Total count
        total_result = await self.session.execute(select(func.count(SolveHistory.id)))
        total_count = total_result.scalar_one()

        # Count grouped by problem_type
        type_query = select(SolveHistory.problem_type, func.count(SolveHistory.id)).group_by(
            SolveHistory.problem_type
        )
        type_result = await self.session.execute(type_query)

        type_counts = {problem_type: count for problem_type, count in type_result.all()}

        return {
            "total_count": total_count,
            "by_problem_type": type_counts,
        }

    async def get_by_id(self, entry_id: int) -> SolveHistory | None:
        """Retrieves a single entry by ID."""
        result = await self.session.execute(select(SolveHistory).where(SolveHistory.id == entry_id))
        return result.scalar_one_or_none()

    async def delete_by_id(self, entry_id: int) -> bool:
        """Deletes an entry by ID. Returns True if deleted, False if not found."""
        entry = await self.get_by_id(entry_id)
        if entry is None:
            return False

        await self.session.delete(entry)
        await self.session.commit()
        return True

    async def clear_all(self) -> int:
        """
        Deletes all history entries using a single SQL DELETE statement.
        Returns the number of rows deleted.
        """
        # First count rows to report deleted count
        count_result = await self.session.execute(select(func.count(SolveHistory.id)))
        count = count_result.scalar_one()

        if count > 0:
            await self.session.execute(delete(SolveHistory))
            await self.session.commit()

        return count
