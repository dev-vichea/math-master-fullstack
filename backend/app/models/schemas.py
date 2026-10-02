"""
Pydantic models that define the API contract described in the project
handoff doc. This file IS the contract your Flutter developer builds
against — keep it stable; add fields rather than renaming/removing them.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    language: Literal["km", "en"] = Field(
        default="km", description="Language of the input question."
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Raw math question, e.g. 'ដោះស្រាយ 2x + 5 = 15'. Maximum 500 characters.",
    )


class SolutionStep(BaseModel):
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
    operation: str | None = (
        None  # Type of operation: "add", "subtract", "multiply", "divide", "factor", etc.
    )
    operands: list[str] = Field(default_factory=list)  # Values involved in operation
    transformation: str | None = (
        None  # What changed: "isolate_variable", "simplify", "expand", etc.
    )
    equation_side: str | None = None  # Which side: "left", "right", "both"


class SolveData(BaseModel):
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
    """Every endpoint returns this envelope, success or failure."""

    success: bool
    data: Any | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
