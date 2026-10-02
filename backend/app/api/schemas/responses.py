"""
API Response Schemas - Pydantic models for API responses.
"""

from typing import Any

from pydantic import BaseModel, Field


class SolutionStep(BaseModel):
    """A single step in the solution process."""

    order: int
    description_km: str
    description_en: str | None = None
    expression: str | None = None

    # Pedagogical explanation metadata ("What" & "Why")
    title_km: str | None = None
    title_en: str | None = None
    rationale_km: str | None = None
    rationale_en: str | None = None
    rule_formula: str | None = None
    is_verification: bool = False

    # Enhanced metadata for operation tracking
    operation: str | None = None  # Type of operation: "add", "subtract", etc.
    operands: list[str] = Field(default_factory=list)  # Values involved
    transformation: str | None = None  # What changed: "isolate_variable", etc.
    equation_side: str | None = None  # Which side: "left", "right", "both"


class SolveData(BaseModel):
    """Complete solution data."""

    problem_type: str
    original_question: str
    detected_intent: str
    normalized_expression: str
    variable: str | None = None
    answer: str | None = None
    is_verified: bool = False
    steps: list[SolutionStep] = Field(default_factory=list)
    lesson_info: dict[str, Any] | None = None


class APIResponse(BaseModel):
    """Standard API response envelope."""

    success: bool
    data: Any | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    app_name: str
    version: str
