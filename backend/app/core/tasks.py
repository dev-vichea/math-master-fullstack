"""
Background task management for long-running operations.

Provides a lightweight abstraction over FastAPI's BackgroundTasks for
operations that shouldn't block the request/response cycle, such as:
  - Large worksheet OCR processing
  - Batch problem solving
  - Result export/report generation

For heavier workloads, this can be extended to use Celery, ARQ, or
any other task queue by swapping the backend implementation.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Coroutine

from app.core.logging import get_logger

logger = get_logger("app.core.tasks")


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Result of a background task."""

    task_id: str
    status: TaskStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    result: Any | None = None
    error: str | None = None
    progress: float = 0.0  # 0.0 to 1.0


# In-memory task store (swap for Redis/DB in production)
_task_store: dict[str, TaskResult] = {}


def create_task_id() -> str:
    """Generate a unique task ID."""
    return f"task_{uuid.uuid4().hex[:12]}"


def get_task(task_id: str) -> TaskResult | None:
    """Retrieve a task result by ID."""
    return _task_store.get(task_id)


async def submit_task(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args: Any,
    task_id: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Submit an async function to run in the background.

    Returns the task ID immediately so the caller can poll for results.

    Usage:
        task_id = await submit_task(process_worksheet, image_bytes, engine=engine)
        # Return task_id to client immediately
        # Client polls GET /api/v1/tasks/{task_id} for status
    """
    tid = task_id or create_task_id()
    _task_store[tid] = TaskResult(task_id=tid, status=TaskStatus.PENDING)

    async def _run() -> None:
        task = _task_store[tid]
        task.status = TaskStatus.RUNNING
        logger.info(f"Task {tid} started: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            logger.info(f"Task {tid} completed successfully")
        except Exception as exc:
            task.error = str(exc)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            logger.error(f"Task {tid} failed: {exc}", exc_info=True)

    asyncio.create_task(_run())
    return tid


def update_task_progress(task_id: str, progress: float) -> None:
    """Update the progress of a running task (0.0 to 1.0)."""
    task = _task_store.get(task_id)
    if task and task.status == TaskStatus.RUNNING:
        task.progress = min(max(progress, 0.0), 1.0)
