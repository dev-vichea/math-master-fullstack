"""
Pluggable interface and calculation building infrastructure.
Each problem type gets its own StepGenerator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import sympy

from app.api.schemas.responses import CalculationItem, SolutionStep


class CalculationBuilder:
    """
    Standard builder for pedagogical multi-line calculations with short
    left-aligned step explanations before transitions.
    """

    def __init__(self, initial_math: str | None = None, label: str | None = None):
        self.items: list[CalculationItem] = []
        if initial_math:
            self.add_initial(initial_math, label=label)

    def add_initial(self, math: str, label: str | None = None) -> CalculationBuilder:
        """Add the starting mathematical state (optionally with a clean initial label)."""
        clean_m = str(math).strip()
        clean_l = str(label).strip() if label else None
        if clean_m:
            self.items.append(CalculationItem(text=clean_l, math=clean_m))
        return self

    def add_step(self, action: str | None, math: str) -> CalculationBuilder:
        """Add a transition action followed by the resulting mathematical expression."""
        clean_m = str(math).strip()
        clean_a = str(action).strip() if action else None
        if clean_m:
            self.items.append(CalculationItem(text=clean_a, math=clean_m))
        return self

    def add_math_only(self, math: str) -> CalculationBuilder:
        """Add a mathematical expression without an explanatory prefix."""
        return self.add_step(None, math)

    def add_note(self, note: str) -> CalculationBuilder:
        """Add a textual pedagogical note without a standalone math equation."""
        clean_n = str(note).strip()
        if clean_n:
            self.items.append(CalculationItem(text=clean_n, math=None))
        return self

    def build_calc_steps(self) -> list[CalculationItem]:
        return list(self.items)

    def build_expression(self) -> str:
        return "\n".join(item.math for item in self.items if item.math)

    def build_details(self) -> list[str]:
        return [item.text for item in self.items if item.text]


def create_solution_step(
    order: int,
    title_km: str,
    description_km: str,
    calc: CalculationBuilder | list[CalculationItem] | str | None = None,
    title_en: str | None = None,
    description_en: str | None = None,
    teacher_note: str | None = None,
    important_note: str | None = None,
    details: list[str] | None = None,
    rule_formula: str | None = None,
    rationale_km: str | None = None,
    rationale_en: str | None = None,
    operation: str | None = None,
    operands: list[str] | None = None,
    transformation: str | None = None,
    equation_side: str | None = None,
    is_verification: bool = False,
) -> SolutionStep:
    """
    Unified architectural factory for creating SolutionStep objects.
    Ensures calc_steps, expression, and details are always synchronized.
    """
    calc_steps: list[CalculationItem] = []
    expr_str: str | None = None
    detail_list: list[str] = list(details or [])

    if isinstance(calc, CalculationBuilder):
        calc_steps = calc.build_calc_steps()
        expr_str = calc.build_expression()
        if not detail_list:
            detail_list = calc.build_details()
    elif isinstance(calc, list):
        calc_steps = calc
        expr_str = "\n".join(item.math for item in calc if item.math)
        if not detail_list:
            detail_list = [item.text for item in calc if item.text]
    elif isinstance(calc, str):
        expr_str = calc

    return SolutionStep(
        order=order,
        title_km=title_km,
        title_en=title_en,
        description_km=description_km,
        description_en=description_en,
        expression=expr_str,
        calc_steps=calc_steps,
        teacher_note=teacher_note,
        important_note=important_note,
        details=detail_list,
        rule_formula=rule_formula,
        rationale_km=rationale_km,
        rationale_en=rationale_en,
        operation=operation,
        operands=operands or [],
        transformation=transformation,
        equation_side=equation_side,
        is_verification=is_verification,
    )


class StepGenerator(ABC):
    problem_type: str

    @abstractmethod
    def generate(self, eq: sympy.Eq, symbol: sympy.Symbol) -> list[SolutionStep]: ...
