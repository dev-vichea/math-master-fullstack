"""
API Response Schemas - Pydantic models for API responses.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class CalculationItem(BaseModel):
    text: str | None = None
    math: str | None = None


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

    # Teacher Persona explanation fields
    teacher_note: str | None = None
    important_note: str | None = None
    details: list[str] = Field(default_factory=list)
    calc_steps: list[CalculationItem] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def populate_and_sanitize(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Sanitize persona terms
            for key in ("teacher_note", "description_km", "title_km", "important_note"):
                val = data.get(key)
                if isinstance(val, str):
                    data[key] = val.replace("ពីលោកគ្រូ", "").replace("លោកគ្រូ", "").strip()

            calc_steps = data.get("calc_steps")
            if not calc_steps:
                expr = data.get("expression")
                details = data.get("details") or []
                if expr and isinstance(expr, str):
                    clean_expr = expr.replace("\\newline", "\n").replace("\\n", "\n")
                    lines = [l.strip() for l in clean_expr.split("\n") if l.strip()]

                    if len(lines) > 1 and len(details) == len(lines) - 1:
                        data["calc_steps"] = [{"text": None, "math": lines[0]}] + [
                            {"text": details[i], "math": lines[i + 1]} for i in range(len(details))
                        ]
                    elif len(lines) > 1 and len(details) == len(lines):
                        data["calc_steps"] = [
                            {"text": details[i], "math": lines[i]} for i in range(len(lines))
                        ]
                    elif len(lines) > 1:
                        data["calc_steps"] = [{"text": None, "math": line} for line in lines]
                    elif len(lines) == 1:
                        data["calc_steps"] = [{"text": None, "math": lines[0]}]
        return data


class SolveData(BaseModel):
    """Complete solution data."""

    problem_type: str
    original_question: str
    detected_intent: str
    normalized_expression: str
    variable: str | None = None
    answer: str | None = None
    is_verified: bool = False
    teacher_header: str | None = "ដំណោះស្រាយ និងការពន្យល់លម្អិត"
    conclusion_km: str | None = None
    conclusion_en: str | None = None
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
