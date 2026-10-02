"""
Tests for context-aware classification.

Tests classification with and without instruction context.
"""

import pytest

from app.classifier.context_aware_classifier import ContextAwareClassifier
from app.models.document import Instruction, InstructionType
from app.parser.math_parser.expression_parser import parse_math_text


class TestContextAwareClassifier:
    """Test context-aware classification."""

    def test_classify_without_context(self):
        """Test classification without instruction context."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("x^2 - 4")

        result = classifier.classify(parsed, instruction=None)

        assert result.problem_type is not None
        assert result.characteristics is not None
        assert not result.used_instruction_context
        assert result.confidence < 0.8  # Lower confidence without context

    def test_classify_factorization_with_factor_instruction(self):
        """Test factorization problem with factor instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("x^2 - 4")

        instruction = Instruction(
            text="ចូរដាក់ជាកត្តាកត់",
            language="km",
            instruction_type=InstructionType.FACTOR,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert "factor" in result.problem_type.lower()
        assert result.used_instruction_context
        assert result.confidence > 0.8  # Higher confidence with context
        assert "instruction" in result.reasoning.lower()

    def test_classify_equation_with_solve_instruction(self):
        """Test equation with solve instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("2x + 5 = 11")

        instruction = Instruction(
            text="ដោះស្រាយសមីការ",
            language="km",
            instruction_type=InstructionType.SOLVE,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert "equation" in result.problem_type.lower()
        assert result.used_instruction_context
        assert result.confidence > 0.8

    def test_classify_linear_equation_with_solve(self):
        """Test linear equation classified with solve instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("3x - 7 = 2")

        instruction = Instruction(
            text="Solve the equation",
            language="en",
            instruction_type=InstructionType.SOLVE,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert result.problem_type == "linear_equation"
        assert result.characteristics.max_polynomial_degree == 1

    def test_classify_quadratic_equation_with_solve(self):
        """Test quadratic equation classified with solve instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("Eq(x^2 - 5*x + 6, 0)")

        instruction = Instruction(
            text="Solve",
            language="en",
            instruction_type=InstructionType.SOLVE,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert result.problem_type == "quadratic_equation"
        assert result.characteristics.max_polynomial_degree == 2

    def test_classify_expression_with_simplify_instruction(self):
        """Test expression with simplify instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("(x + 1)(x - 1)")

        instruction = Instruction(
            text="Simplify",
            language="en",
            instruction_type=InstructionType.SIMPLIFY,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert "simplif" in result.problem_type.lower()
        assert result.used_instruction_context

    def test_classify_expression_with_expand_instruction(self):
        """Test expression with expand instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("(x + 2)(x - 3)")

        instruction = Instruction(
            text="Expand",
            language="en",
            instruction_type=InstructionType.EXPAND,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert "expand" in result.problem_type.lower() or "expansion" in result.problem_type.lower()

    def test_classify_with_unknown_instruction(self):
        """Test classification with unknown instruction type."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("x^2 - 4")

        instruction = Instruction(
            text="Do something",
            language="en",
            instruction_type=InstructionType.UNKNOWN,
        )

        result = classifier.classify(parsed, instruction=instruction)

        # Should fall back to base classification
        assert not result.used_instruction_context
        assert result.confidence < 0.8

    def test_classify_batch_with_shared_instruction(self):
        """Test batch classification with shared instruction."""
        classifier = ContextAwareClassifier()

        expressions = [
            parse_math_text("x^2 - 4"),
            parse_math_text("x^2 - 5*x + 6"),
            parse_math_text("2*x^2 + 8*x"),
        ]

        instruction = Instruction(
            text="Factor",
            language="en",
            instruction_type=InstructionType.FACTOR,
        )

        results = classifier.classify_batch(expressions, instruction=instruction)

        assert len(results) == 3
        for result in results:
            assert "factor" in result.problem_type.lower()
            assert result.used_instruction_context

    def test_get_expected_types(self):
        """Test getting expected problem types for instruction."""
        classifier = ContextAwareClassifier()

        factor_types = classifier.get_expected_types(InstructionType.FACTOR)
        assert "polynomial_factorization" in factor_types

        solve_types = classifier.get_expected_types(InstructionType.SOLVE)
        assert "linear_equation" in solve_types
        assert "quadratic_equation" in solve_types

    def test_is_compatible(self):
        """Test checking compatibility between problem and instruction types."""
        classifier = ContextAwareClassifier()

        # Compatible
        assert classifier.is_compatible("polynomial_factorization", InstructionType.FACTOR)
        assert classifier.is_compatible("linear_equation", InstructionType.SOLVE)

        # Not compatible
        assert not classifier.is_compatible("linear_equation", InstructionType.FACTOR)

    def test_confidence_higher_with_context(self):
        """Test that confidence is higher with instruction context."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("x^2 - 4")

        # Without context
        result_no_context = classifier.classify(parsed, instruction=None)

        # With context
        instruction = Instruction(
            text="Factor",
            language="en",
            instruction_type=InstructionType.FACTOR,
        )
        result_with_context = classifier.classify(parsed, instruction=instruction)

        assert result_with_context.confidence > result_no_context.confidence

    def test_refinement_reasoning(self):
        """Test that reasoning explains refinement."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("x^2 - 5*x + 6")

        instruction = Instruction(
            text="Factor",
            language="en",
            instruction_type=InstructionType.FACTOR,
        )

        result = classifier.classify(parsed, instruction=instruction)

        # Reasoning should mention instruction or refinement
        assert len(result.reasoning) > 0
        assert (
            "instruction" in result.reasoning.lower()
            or "factor" in result.reasoning.lower()
        )

    def test_polynomial_degree_detection(self):
        """Test that polynomial degree is correctly detected."""
        classifier = ContextAwareClassifier()

        # Linear
        linear = parse_math_text("Eq(2*x + 5, 11)")
        instruction_solve = Instruction(
            text="Solve",
            language="en",
            instruction_type=InstructionType.SOLVE,
        )
        result_linear = classifier.classify(linear, instruction=instruction_solve)
        assert result_linear.problem_type == "linear_equation"

        # Quadratic
        quadratic = parse_math_text("Eq(x^2 - 5*x + 6, 0)")
        result_quad = classifier.classify(quadratic, instruction=instruction_solve)
        assert result_quad.problem_type == "quadratic_equation"

    def test_fraction_simplification_with_simplify(self):
        """Test fraction expression with simplify instruction."""
        classifier = ContextAwareClassifier()
        parsed = parse_math_text("(x^2 - 4)/(x - 2)")

        instruction = Instruction(
            text="Simplify",
            language="en",
            instruction_type=InstructionType.SIMPLIFY,
        )

        result = classifier.classify(parsed, instruction=instruction)

        assert "simplif" in result.problem_type.lower()
        assert result.characteristics.has_fractions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
