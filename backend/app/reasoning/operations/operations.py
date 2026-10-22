"""
Mathematical operation definitions for step-by-step reasoning.

This module defines standard mathematical operations that can be tracked
throughout the solving process. Each operation has:
- A type identifier
- A transformation description
- Template for explanation generation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OperationType(str, Enum):
    """Standard mathematical operations."""

    # Arithmetic operations
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

    # Algebraic operations
    MOVE_TERM = "move_term"
    COMBINE_LIKE_TERMS = "combine_like_terms"
    FACTOR = "factor"
    EXPAND = "expand"
    SIMPLIFY = "simplify"

    # Equation solving
    ISOLATE_VARIABLE = "isolate_variable"
    SUBSTITUTE = "substitute"
    APPLY_QUADRATIC_FORMULA = "apply_quadratic_formula"
    COMPLETE_SQUARE = "complete_square"

    # Inequality operations
    REVERSE_INEQUALITY = "reverse_inequality"

    # Verification
    VERIFY_SUBSTITUTION = "verify_substitution"
    CHECK_SOLUTION = "check_solution"

    # General
    INITIAL_STATE = "initial_state"
    FINAL_ANSWER = "final_answer"
    INTERMEDIATE_STEP = "intermediate_step"


class TransformationType(str, Enum):
    """Types of mathematical transformations."""

    SIMPLIFICATION = "simplify"
    ISOLATION = "isolate_variable"
    FACTORIZATION = "factor"
    EXPANSION = "expand"
    SUBSTITUTION = "substitute"
    REDUCTION = "reduce"
    NORMALIZATION = "normalize"
    VERIFICATION = "verify"


@dataclass
class OperationMetadata:
    """
    Metadata describing a mathematical operation in a solution step.

    This provides machine-readable information about what happened in each step,
    enabling better explanation generation and step validation.
    """

    operation: OperationType
    operands: list[str]
    transformation: TransformationType | None = None
    equation_side: str | None = None  # "left", "right", "both"
    notes: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "operation": self.operation.value,
            "operands": self.operands,
            "transformation": self.transformation.value if self.transformation else None,
            "equation_side": self.equation_side,
            "notes": self.notes or [],
        }

    @classmethod
    def create_arithmetic(
        cls,
        operation: OperationType,
        value: str,
        side: str = "both",
    ) -> OperationMetadata:
        """Create metadata for basic arithmetic operation."""
        return cls(
            operation=operation,
            operands=[value],
            equation_side=side,
        )

    @classmethod
    def create_isolation(
        cls,
        variable: str,
        operation: OperationType,
        value: str,
    ) -> OperationMetadata:
        """Create metadata for variable isolation step."""
        return cls(
            operation=operation,
            operands=[variable, value],
            transformation=TransformationType.ISOLATION,
        )

    @classmethod
    def create_substitution(
        cls,
        variable: str,
        value: str,
    ) -> OperationMetadata:
        """Create metadata for substitution step."""
        return cls(
            operation=OperationType.SUBSTITUTE,
            operands=[variable, value],
            transformation=TransformationType.SUBSTITUTION,
        )


def get_operation_template_key(operation: OperationType) -> str:
    """
    Get template key for explanation generation.

    Maps operation types to template keys used in localization system.
    """
    template_map = {
        OperationType.ADD: "add_to_both_sides",
        OperationType.SUBTRACT: "subtract_from_both_sides",
        OperationType.MULTIPLY: "multiply_both_sides",
        OperationType.DIVIDE: "divide_both_sides",
        OperationType.MOVE_TERM: "move_term_to_side",
        OperationType.COMBINE_LIKE_TERMS: "combine_like_terms",
        OperationType.ISOLATE_VARIABLE: "isolate_variable",
        OperationType.SUBSTITUTE: "substitute_value",
        OperationType.APPLY_QUADRATIC_FORMULA: "apply_quadratic_formula",
        OperationType.REVERSE_INEQUALITY: "reverse_inequality_sign",
        OperationType.INITIAL_STATE: "original_equation",
        OperationType.FINAL_ANSWER: "final_answer",
    }
    return template_map.get(operation, "step")


class StepBuilder:
    """
    Helper class for building solution steps with operation metadata.

    Simplifies the creation of SolutionStep objects with proper metadata.
    """

    def __init__(self, step_number: int = 1):
        """Initialize step builder."""
        self.step_number = step_number

    def create_step(
        self,
        description_km: str,
        description_en: str,
        expression: str,
        operation: OperationType,
        operands: list[str] | None = None,
        transformation: TransformationType | None = None,
        equation_side: str | None = None,
        title_km: str | None = None,
        title_en: str | None = None,
        teacher_note: str | None = None,
        important_note: str | None = None,
        details: list[str] | None = None,
        calc_steps: list[dict[str, Any]] | None = None,
        rule_formula: str | None = None,
        rationale_km: str | None = None,
        rationale_en: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a solution step with full metadata.

        Returns a dictionary matching SolutionStep schema.
        """
        # Automatically construct calc_steps if not explicitly given
        formatted_calc_steps = list(calc_steps or [])
        if not formatted_calc_steps and expression:
            lines = [l.strip() for l in expression.split("\n") if l.strip()]
            if len(lines) > 1 and details and len(details) == len(lines) - 1:
                formatted_calc_steps = [{"text": None, "math": lines[0]}]
                for idx, line in enumerate(lines[1:]):
                    formatted_calc_steps.append({"text": details[idx], "math": line})
            elif len(lines) > 1:
                formatted_calc_steps = [{"text": None, "math": line} for line in lines]
            elif len(lines) == 1:
                formatted_calc_steps = [{"text": None, "math": lines[0]}]

        step = {
            "order": self.step_number,
            "description_km": description_km,
            "description_en": description_en,
            "expression": expression,
            "operation": operation.value,
            "operands": operands or [],
            "transformation": transformation.value if transformation else None,
            "equation_side": equation_side,
            "title_km": title_km,
            "title_en": title_en,
            "teacher_note": teacher_note,
            "important_note": important_note,
            "details": details or [],
            "calc_steps": formatted_calc_steps,
            "rule_formula": rule_formula,
            "rationale_km": rationale_km,
            "rationale_en": rationale_en,
        }

        self.step_number += 1
        return step

    def create_initial_step(
        self,
        expression: str,
        description_km: str = "សមីការដើម៖",
        description_en: str = "Original equation:",
        title_km: str = "សមីការដើម",
        title_en: str = "Original Equation",
        teacher_note: str | None = None,
        important_note: str | None = None,
        details: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create initial state step."""
        return self.create_step(
            description_km=description_km,
            description_en=description_en,
            expression=expression,
            operation=OperationType.INITIAL_STATE,
            title_km=title_km,
            title_en=title_en,
            teacher_note=teacher_note,
            important_note=important_note,
            details=details,
        )

    def create_arithmetic_step(
        self,
        operation: OperationType,
        value: str,
        expression: str,
        description_km: str,
        description_en: str,
        side: str = "both",
        title_km: str | None = None,
        title_en: str | None = None,
        teacher_note: str | None = None,
        important_note: str | None = None,
        details: list[str] | None = None,
        rule_formula: str | None = None,
    ) -> dict[str, Any]:
        """Create arithmetic operation step."""
        return self.create_step(
            description_km=description_km,
            description_en=description_en,
            expression=expression,
            operation=operation,
            operands=[value],
            equation_side=side,
            title_km=title_km,
            title_en=title_en,
            teacher_note=teacher_note,
            important_note=important_note,
            details=details,
            rule_formula=rule_formula,
        )

    def create_final_step(
        self,
        expression: str,
        description_km: str,
        description_en: str,
        title_km: str = "ចម្លើយចុងក្រោយ",
        title_en: str = "Final Answer",
        teacher_note: str | None = None,
        important_note: str | None = None,
        details: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create final answer step."""
        return self.create_step(
            description_km=description_km,
            description_en=description_en,
            expression=expression,
            operation=OperationType.FINAL_ANSWER,
            title_km=title_km,
            title_en=title_en,
            teacher_note=teacher_note,
            important_note=important_note,
            details=details,
        )

    def create_step_from_template(
        self,
        operation: OperationType,
        expression: str,
        transformation: TransformationType | None = None,
        equation_side: str | None = None,
        **template_vars: Any,
    ) -> dict[str, Any]:
        """
        Create a solution step using the template-based explanation generator.

        This method automatically generates bilingual descriptions using templates,
        ensuring consistency and avoiding manual Khmer/English string duplication.

        Args:
            operation: The operation type
            expression: The resulting mathematical expression
            transformation: Optional transformation type
            equation_side: Optional equation side ("left", "right", "both")
            **template_vars: Variables to fill into templates (value, variable, etc.)

        Returns:
            Dictionary matching SolutionStep schema

        Example:
            >>> builder = StepBuilder()
            >>> builder.create_step_from_template(
            ...     operation=OperationType.ADD,
            ...     expression="2x = 10",
            ...     value="5",
            ...     side="both",
            ... )
        """
        # Import here to avoid circular dependency
        from app.explanation.templates.templates import get_explanation_generator

        gen = get_explanation_generator()

        # Generate bilingual descriptions
        description_km = gen.generate_step_description(
            operation,
            language="km",
            **template_vars,
        )
        description_en = gen.generate_step_description(
            operation,
            language="en",
            **template_vars,
        )

        # Extract operands from template vars
        operands = []
        if "value" in template_vars:
            operands.append(str(template_vars["value"]))
        if "variable" in template_vars and "value" not in template_vars:
            operands.append(str(template_vars["variable"]))

        return self.create_step(
            description_km=description_km,
            description_en=description_en,
            expression=expression,
            operation=operation,
            operands=operands,
            transformation=transformation,
            equation_side=equation_side,
        )
