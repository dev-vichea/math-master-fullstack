"""
History endpoints for managing and inspecting past math solutions.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.models.schemas import APIResponse
from app.services.history_service import HistoryService, get_history_service

router = APIRouter()


@router.get("/math/history", response_model=APIResponse, tags=["history"])
async def get_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip (for pagination)"),
    problem_type: str | None = Query(
        None, description="Filter by problem type (e.g., 'linear_equation')"
    ),
    date_from: datetime | None = Query(
        None, description="Filter entries created after this datetime (ISO 8601)"
    ),
    date_to: datetime | None = Query(
        None, description="Filter entries created before this datetime (ISO 8601)"
    ),
    search: str | None = Query(None, description="Search in question text (case-insensitive)"),
    history_service: HistoryService = Depends(get_history_service),
) -> APIResponse:
    """
    Get history of solved math problems with filtering and pagination.
    """
    entries, total_count = await history_service.list_entries(
        limit=limit,
        offset=offset,
        problem_type=problem_type,
        date_from=date_from,
        date_to=date_to,
        search_query=search,
    )

    items = [
        {
            "id": entry.id,
            "question": entry.question,
            "problem_type": entry.problem_type,
            "normalized_expression": entry.normalized_expression,
            "answer": entry.answer,
            "is_verified": entry.is_verified,
            "steps": entry.steps_json,
            "created_at": entry.created_at.isoformat(),
        }
        for entry in entries
    ]

    has_more = (offset + len(items)) < total_count

    response_data = {
        "items": items,
        "pagination": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "returned_count": len(items),
            "has_more": has_more,
        },
    }

    return APIResponse(success=True, data=response_data, error=None)


@router.get("/math/history/stats", response_model=APIResponse, tags=["history"])
async def get_stats(
    history_service: HistoryService = Depends(get_history_service),
) -> APIResponse:
    """
    Get aggregate statistics about history entries (total count and count by problem type).
    """
    stats = await history_service.get_stats()
    return APIResponse(success=True, data=stats, error=None)


@router.delete("/math/history/{entry_id}", response_model=APIResponse, tags=["history"])
async def delete_entry(
    entry_id: int,
    history_service: HistoryService = Depends(get_history_service),
) -> APIResponse:
    """
    Delete a specific history entry by ID.
    """
    deleted = await history_service.delete_entry(entry_id)

    if not deleted:
        return APIResponse(
            success=False,
            data=None,
            error=f"History entry with ID {entry_id} not found",
        )

    return APIResponse(
        success=True,
        data={"deleted_id": entry_id},
        error=None,
    )


@router.delete("/math/history", response_model=APIResponse, tags=["history"])
async def clear_history(
    history_service: HistoryService = Depends(get_history_service),
) -> APIResponse:
    """
    Clear all history entries.
    """
    count = await history_service.clear_all()

    return APIResponse(
        success=True,
        data={"deleted_count": count},
        error=None,
    )
