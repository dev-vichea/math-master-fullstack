"""SQLAlchemy 2.0 ORM models. Kept separate from app/models/schemas.py
(the Pydantic API models) on purpose: the API contract and the storage
layer are allowed to evolve independently."""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SolveHistory(Base):
    """One row per solved question — backs the mobile app's 'History' tab."""

    __tablename__ = "solve_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    problem_type: Mapped[str] = mapped_column(String(64))
    normalized_expression: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    steps_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
