"""
Template-based explanation generator for mathematical operations.

This module provides deterministic, LLM-free bilingual (Khmer/English) explanations
for mathematical steps. Each operation type has predefined templates that can be
filled with actual values from the solving process.

Architecture:
- ExplanationGenerator: Main class for generating explanations
- Operation templates: Khmer and English templates for each operation type
- Number formatting: Proper formatting for fractions, decimals, negatives in both languages
- Context awareness: Templates adapt based on equation side, operation context, etc.
"""

from __future__ import annotations

from typing import Any

from app.core.engine.operations import OperationType, TransformationType


class NumberFormatter:
    """Formats numbers for Khmer and English mathematical explanations."""

    @staticmethod
    def format_km(value: Any) -> str:
        """
        Format a number/expression for Khmer display.

        Examples:
            2 -> "២"
            -3 -> "-៣"
            1/2 -> "១/២"
            0.5 -> "០.៥"
        """
        value_str = str(value)

        # Map ASCII digits to Khmer digits
        khmer_digits = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")

        # Keep mathematical operators unchanged
        return value_str.translate(khmer_digits)

    @staticmethod
    def format_en(value: Any) -> str:
        """Format a number/expression for English display."""
        return str(value)


class ExplanationGenerator:
    """
    Generates bilingual mathematical step explanations using templates.

    This is a deterministic, template-based system that does NOT use LLMs.
    Each operation type maps to predefined Khmer and English templates.
    """

    def __init__(self):
        self.formatter = NumberFormatter()
        self._operation_templates = self._build_operation_templates()
        self._transformation_templates = self._build_transformation_templates()

    def _build_operation_templates(self) -> dict[OperationType, dict[str, str]]:
        """
        Build templates for each operation type.

        Template variables (use {var} format):
        - {value}: The numeric value being operated with
        - {variable}: The algebraic variable (x, y, etc.)
        - {expression}: The resulting expression
        - {side}: Which side (left, right, both)
        - {from_expr}: Starting expression
        - {to_expr}: Ending expression
        """
        return {
            # Arithmetic operations
            OperationType.ADD: {
                "km": "បូក {value} ទៅភាគីទាំងពីរ",
                "en": "Add {value} to both sides",
                "km_single": "បូក {value}",
                "en_single": "Add {value}",
            },
            OperationType.SUBTRACT: {
                "km": "ដក {value} ពីភាគីទាំងពីរ",
                "en": "Subtract {value} from both sides",
                "km_single": "ដក {value}",
                "en_single": "Subtract {value}",
            },
            OperationType.MULTIPLY: {
                "km": "គុណភាគីទាំងពីរដោយ {value}",
                "en": "Multiply both sides by {value}",
                "km_single": "គុណដោយ {value}",
                "en_single": "Multiply by {value}",
            },
            OperationType.DIVIDE: {
                "km": "ចែកភាគីទាំងពីរដោយ {value}",
                "en": "Divide both sides by {value}",
                "km_single": "ចែកដោយ {value}",
                "en_single": "Divide by {value}",
            },
            # Algebraic operations
            OperationType.MOVE_TERM: {
                "km": "ផ្លាស់ទី {value} ទៅ{side}",
                "en": "Move {value} to the {side} side",
                "km_all_left": "ផ្លាស់ទី {variable} ទាំងអស់មកខាងឆ្វេង",
                "en_all_left": "Move all {variable} terms to the left side",
                "km_all_right": "ផ្លាស់ទីអថេរទៅខាងស្តាំ",
                "en_all_right": "Move constants to the right side",
            },
            OperationType.COMBINE_LIKE_TERMS: {
                "km": "បូកពាក្យដូចគ្នា",
                "en": "Combine like terms",
                "km_simplify": "សាមញ្ញធ្វើ {from_expr} ទៅជា {to_expr}",
                "en_simplify": "Simplify {from_expr} to {to_expr}",
            },
            OperationType.EXPAND: {
                "km": "ពង្រីក {from_expr}",
                "en": "Expand {from_expr}",
                "km_distribute": "បែងចែក {value}",
                "en_distribute": "Distribute {value}",
            },
            OperationType.FACTOR: {
                "km": "កត្តា {from_expr}",
                "en": "Factor {from_expr}",
                "km_common": "យកកត្តារួម {value}",
                "en_common": "Factor out {value}",
            },
            # Equation solving
            OperationType.ISOLATE_VARIABLE: {
                "km": "កំណត់តែ {variable}",
                "en": "Isolate {variable}",
                "km_solve_for": "ដោះស្រាយរក {variable}",
                "en_solve_for": "Solve for {variable}",
            },
            OperationType.SUBSTITUTE: {
                "km": "ជំនួស {variable} ដោយ {value}",
                "en": "Substitute {variable} with {value}",
            },
            # Quadratic-specific
            OperationType.APPLY_QUADRATIC_FORMULA: {
                "km": "ប្រើរូបមន្តការេ៉",
                "en": "Apply quadratic formula",
                "km_full": "ប្រើរូបមន្ត x = (-b ± √(b²-4ac)) / (2a)",
                "en_full": "Apply formula x = (-b ± √(b²-4ac)) / (2a)",
            },
            OperationType.COMPLETE_SQUARE: {
                "km": "បំពេញការេ៉",
                "en": "Complete the square",
            },
            # Special operations
            OperationType.SIMPLIFY: {
                "km": "សាមញ្ញធ្វើ",
                "en": "Simplify",
                "km_expression": "សាមញ្ញធ្វើកន្សោម",
                "en_expression": "Simplify expression",
            },
            OperationType.VERIFY_SUBSTITUTION: {
                "km": "ផ្ទៀងផ្ទាត់ចម្លើយ",
                "en": "Verify solution",
                "km_check": "ពិនិត្យ៖ {from_expr} = {to_expr}",
                "en_check": "Check: {from_expr} = {to_expr}",
            },
            OperationType.CHECK_SOLUTION: {
                "km": "ពិនិត្យដំណោះស្រាយ",
                "en": "Check solution",
            },
            # Inequality
            OperationType.REVERSE_INEQUALITY: {
                "km": "ប្តូរទិសនៃវិសមភាព",
                "en": "Reverse inequality direction",
            },
            # Final answer
            OperationType.FINAL_ANSWER: {
                "km": "ចម្លើយ៖ {answer}",
                "en": "Answer: {answer}",
                "km_solution": "ដំណោះស្រាយ៖ {answer}",
                "en_solution": "Solution: {answer}",
            },
        }

    def _build_transformation_templates(self) -> dict[TransformationType, dict[str, str]]:
        """Build templates for transformation descriptions."""
        return {
            TransformationType.ISOLATION: {
                "km": "កំណត់អថេរនៅម្ខាង",
                "en": "Isolating the variable",
            },
            TransformationType.SIMPLIFICATION: {
                "km": "សាមញ្ញធ្វើកន្សោម",
                "en": "Simplifying",
            },
            TransformationType.EXPANSION: {
                "km": "ពង្រីកកន្សោម",
                "en": "Expanding",
            },
            TransformationType.FACTORIZATION: {
                "km": "កត្តារូបមន្ត",
                "en": "Factoring",
            },
            TransformationType.NORMALIZATION: {
                "km": "រៀបចំឡើងវិញ",
                "en": "Rearranging",
            },
            TransformationType.SUBSTITUTION: {
                "km": "ជំនួស",
                "en": "Substituting",
            },
            TransformationType.VERIFICATION: {
                "km": "ផ្ទៀងផ្ទាត់",
                "en": "Verifying",
            },
        }

    def generate_step_description(
        self,
        operation: OperationType | str,
        language: str = "km",
        **kwargs: Any,
    ) -> str:
        """
        Generate a step description in the specified language.

        Args:
            operation: The operation type (from OperationType enum or string)
            language: "km" for Khmer, "en" for English
            **kwargs: Template variables (value, variable, expression, etc.)

        Returns:
            Formatted description string

        Examples:
            >>> gen = ExplanationGenerator()
            >>> gen.generate_step_description(
            ...     OperationType.ADD,
            ...     language="km",
            ...     value="3",
            ... )
            "បូក ៣ ទៅភាគីទាំងពីរ"
        """
        # Convert string to OperationType if needed
        if isinstance(operation, str):
            try:
                operation = OperationType(operation)
            except ValueError:
                # Fallback for unknown operations
                return kwargs.get("description", f"Unknown operation: {operation}")

        # Get templates for this operation
        templates = self._operation_templates.get(operation, {})

        # Determine which template variant to use
        template_key = self._select_template_variant(templates, language, kwargs)
        template = templates.get(template_key, "")

        if not template:
            # Fallback if template not found
            return kwargs.get("description", f"Perform {operation.value}")

        # Format numbers based on language
        formatted_kwargs = self._format_template_variables(kwargs, language)

        # Fill template with variables
        try:
            return template.format(**formatted_kwargs)
        except KeyError:
            # Missing required variable - return template as-is
            return template

    def _select_template_variant(
        self,
        templates: dict[str, str],
        language: str,
        context: dict[str, Any],
    ) -> str:
        """
        Select the appropriate template variant based on context.

        Some operations have multiple template variants:
        - "km" / "en": Default template
        - "km_single" / "en_single": Single-side operation
        - "km_all_left" / "en_all_left": Moving all terms left
        - etc.
        """
        # Check for specific context flags
        if context.get("side") == "both":
            key = language
        elif context.get("side") in ("left", "right", "single"):
            key = f"{language}_single"
            if key not in templates:
                key = language
        elif context.get("move_all_left"):
            key = f"{language}_all_left"
            if key not in templates:
                key = language
        elif context.get("variant"):
            # Explicit variant requested
            key = f"{language}_{context['variant']}"
            if key not in templates:
                key = language
        else:
            key = language

        return key

    def _format_template_variables(
        self,
        variables: dict[str, Any],
        language: str,
    ) -> dict[str, str]:
        """Format all template variables for the target language."""
        formatted = {}
        formatter = self.formatter.format_km if language == "km" else self.formatter.format_en

        for key, value in variables.items():
            if isinstance(value, (int, float, str)):
                # Format numeric values
                if key in ("value", "answer", "from_expr", "to_expr"):
                    formatted[key] = formatter(value)
                else:
                    # Non-numeric values (like "left", "right", "both")
                    formatted[key] = self._translate_keyword(str(value), language)
            else:
                formatted[key] = str(value)

        return formatted

    def _translate_keyword(self, keyword: str, language: str) -> str:
        """Translate common keywords like 'left', 'right', 'both' to target language."""
        if language == "km":
            translations = {
                "left": "ខាងឆ្វេង",
                "right": "ខាងស្តាំ",
                "both": "ទាំងពីរ",
                "side": "ភាគី",
            }
            return translations.get(keyword.lower(), keyword)
        return keyword

    def generate_operation_summary(
        self,
        operation: OperationType | str,
        language: str = "km",
    ) -> str:
        """
        Generate a brief summary of what an operation does.

        Useful for metadata and documentation.
        """
        if isinstance(operation, str):
            try:
                operation = OperationType(operation)
            except ValueError:
                return operation

        summaries = {
            "km": {
                OperationType.ADD: "ប្រមាណវិធីបូក",
                OperationType.SUBTRACT: "ប្រមាណវិធីដក",
                OperationType.MULTIPLY: "ប្រមាណវិធីគុណ",
                OperationType.DIVIDE: "ប្រមាណវិធីចែក",
                OperationType.ISOLATE_VARIABLE: "កំណត់អថេរ",
                OperationType.SIMPLIFY: "សាមញ្ញធ្វើ",
                OperationType.FACTOR: "កត្តារូបមន្ត",
                OperationType.EXPAND: "ពង្រីករូបមន្ត",
                OperationType.APPLY_QUADRATIC_FORMULA: "រូបមន្តការេ៉",
            },
            "en": {
                OperationType.ADD: "Addition operation",
                OperationType.SUBTRACT: "Subtraction operation",
                OperationType.MULTIPLY: "Multiplication operation",
                OperationType.DIVIDE: "Division operation",
                OperationType.ISOLATE_VARIABLE: "Variable isolation",
                OperationType.SIMPLIFY: "Simplification",
                OperationType.FACTOR: "Factorization",
                OperationType.EXPAND: "Expansion",
                OperationType.APPLY_QUADRATIC_FORMULA: "Quadratic formula",
            },
        }

        lang_summaries = summaries.get(language, summaries["en"])
        return lang_summaries.get(operation, operation.value)

    def format_expression_with_explanation(
        self,
        expression: str,
        operation: OperationType | str,
        language: str = "km",
        **kwargs: Any,
    ) -> tuple[str, str]:
        """
        Generate both the formatted expression and its explanation.

        Returns:
            Tuple of (expression, description)
        """
        description = self.generate_step_description(operation, language, **kwargs)

        # Format expression for the target language
        if language == "km":
            formatted_expr = self.formatter.format_km(expression)
        else:
            formatted_expr = self.formatter.format_en(expression)

        return formatted_expr, description


# Global singleton instance for convenience
_generator = ExplanationGenerator()


def get_explanation_generator() -> ExplanationGenerator:
    """Get the global ExplanationGenerator instance."""
    return _generator


def generate_bilingual_step(
    operation: OperationType | str,
    expression: str,
    **kwargs: Any,
) -> dict[str, str]:
    """
    Convenience function to generate both Khmer and English descriptions.

    Returns:
        Dictionary with keys: description_km, description_en, expression
    """
    gen = get_explanation_generator()

    return {
        "description_km": gen.generate_step_description(operation, "km", **kwargs),
        "description_en": gen.generate_step_description(operation, "en", **kwargs),
        "expression": expression,
    }
