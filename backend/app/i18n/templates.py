"""
Bilingual Explanation Templates and Step Builders for Khmer and English.

Provides deterministic, LLM-free explanation generators and step builders
that produce complete SolutionStep objects with Khmer and English descriptions,
pedagogical titles, rationales, and operation tracking.
"""

from __future__ import annotations

from typing import Any

from app.api.schemas.responses import SolutionStep
from app.explanation.templates.templates import (
    ExplanationGenerator,
    generate_bilingual_step,
    get_explanation_generator,
)
from app.i18n.locales import Language, normalize_language


def create_bilingual_step(
    order: int,
    expression: str | None = None,
    description_km: str = "",
    description_en: str = "",
    title_km: str | None = None,
    title_en: str | None = None,
    rationale_km: str | None = None,
    rationale_en: str | None = None,
    rule_formula: str | None = None,
    is_verification: bool = False,
    operation: str | None = None,
    operands: list[str] | None = None,
    transformation: str | None = None,
    equation_side: str | None = None,
) -> SolutionStep:
    """
    Construct a validated SolutionStep instance with full bilingual fields.

    Args:
        order: Step sequence number (1-indexed)
        expression: Resulting math expression/equation at this step
        description_km: Primary Khmer step explanation
        description_en: English translation of step explanation
        title_km: Pedagogical header in Khmer (e.g. "សមីការដើម")
        title_en: Pedagogical header in English (e.g. "Initial equation")
        rationale_km: Educational 'Why' justification in Khmer
        rationale_en: Educational 'Why' justification in English
        rule_formula: Applied theorem or formula LaTeX
        is_verification: True if step represents solution check
        operation: Operation identifier (e.g. "add", "divide", "factor")
        operands: Operands involved (e.g. ["5", "both"])
        transformation: Transformation identifier
        equation_side: Equation side affected ("left", "right", "both")

    Returns:
        SolutionStep model
    """
    return SolutionStep(
        order=order,
        description_km=description_km,
        description_en=description_en or None,
        expression=expression,
        title_km=title_km,
        title_en=title_en,
        rationale_km=rationale_km,
        rationale_en=rationale_en,
        rule_formula=rule_formula,
        is_verification=is_verification,
        operation=operation,
        operands=operands or [],
        transformation=transformation,
        equation_side=equation_side,
    )


def localize_solution_step(
    step: SolutionStep | dict[str, Any],
    lang: str | Language = Language.KM,
) -> dict[str, Any]:
    """
    Transform a bilingual step into a localized representation targeting a single language,
    while keeping the underlying data structure intact.
    """
    step_dict = step.model_dump() if isinstance(step, SolutionStep) else dict(step)
    target_lang = normalize_language(lang)

    if target_lang == Language.KM:
        step_dict["description"] = step_dict.get("description_km") or step_dict.get("description_en", "")
        step_dict["title"] = step_dict.get("title_km") or step_dict.get("title_en")
        step_dict["rationale"] = step_dict.get("rationale_km") or step_dict.get("rationale_en")
    else:
        step_dict["description"] = step_dict.get("description_en") or step_dict.get("description_km", "")
        step_dict["title"] = step_dict.get("title_en") or step_dict.get("title_km")
        step_dict["rationale"] = step_dict.get("rationale_en") or step_dict.get("rationale_km")

    return step_dict


__all__ = [
    "ExplanationGenerator",
    "get_explanation_generator",
    "generate_bilingual_step",
    "create_bilingual_step",
    "localize_solution_step",
]
