"""
Enhanced problem classifier with comprehensive detection capabilities.

This module provides detailed problem type classification and characteristic
detection for mathematical problems. It goes beyond simple equation degree
checking to identify:
- Specific problem categories (fractions, percentages, ratios)
- Mathematical operations (factorization, simplification, expansion)
- Advanced topics (trigonometry, calculus, complex numbers)
- Problem characteristics for solver selection

The classifier returns both a problem_type string (for solver routing) and
detailed ProblemCharacteristics (for analysis and UI hints).
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import (
    Abs,
    Derivative,
    Eq,
    Float,
    I,
    Integral,
    Limit,
    Poly,
    Rational,
    Symbol,
    cos,
    expand,
    sin,
    sqrt,
    tan,
)
from sympy.core.relational import Relational

from app.core.parser.expression_parser import ParsedMath
from app.models.problem import ProblemCharacteristics


class ProblemClassifier:
    """
    Enhanced classifier for mathematical problems.

    Provides comprehensive detection of problem types and characteristics
    to guide solver selection and provide better user feedback.
    """

    def __init__(self):
        """Initialize classifier with detection patterns."""
        # Trigonometric functions
        self.trig_functions = {
            sin,
            cos,
            tan,
            sympy.sec,
            sympy.csc,
            sympy.cot,
            sympy.asin,
            sympy.acos,
            sympy.atan,
        }

        # Calculus operations
        self.calculus_operations = {Derivative, Integral, Limit}

    def classify(
        self, parsed: ParsedMath, detect_characteristics: bool = True
    ) -> tuple[str, ProblemCharacteristics | None]:
        """
        Classify a parsed mathematical expression.

        Args:
            parsed: ParsedMath object from parser
            detect_characteristics: Whether to analyze problem characteristics

        Returns:
            Tuple of (problem_type, characteristics)
        """
        expr = parsed.sympy_expr
        characteristics = ProblemCharacteristics() if detect_characteristics else None

        # Detect characteristics first
        if characteristics:
            self._detect_characteristics(expr, parsed.symbols, characteristics)

        # Classify by problem type
        problem_type = self._classify_problem_type(expr, parsed, characteristics)

        return problem_type, characteristics

    def _detect_characteristics(
        self, expr: Any, symbols: list[Symbol], chars: ProblemCharacteristics
    ) -> None:
        """Analyze expression to detect mathematical characteristics."""

        # Basic structure
        chars.variable_count = len(symbols)
        chars.has_equation = isinstance(expr, Eq)
        chars.has_inequality = isinstance(expr, Relational) and not isinstance(expr, Eq)

        # Convert to string for pattern detection
        expr_str = str(expr)

        # Detect fractions
        if isinstance(expr, Rational) or "/" in expr_str:
            chars.has_fractions = True

        # Check all sub-expressions
        if hasattr(expr, "atoms"):
            atoms = expr.atoms()

            # Detect complex numbers
            if I in atoms or any(hasattr(a, "is_imaginary") and a.is_imaginary for a in atoms):
                chars.has_complex_numbers = True

            # Detect trigonometry
            for atom in atoms:
                if type(atom) in self.trig_functions:
                    chars.has_trigonometry = True
                    break

            # Detect calculus
            for atom in atoms:
                if type(atom) in self.calculus_operations:
                    chars.has_calculus = True
                    break

        # Detect exponents/radicals
        if hasattr(expr, "as_ordered_factors"):
            for factor in expr.as_ordered_factors():
                if hasattr(factor, "exp") or isinstance(factor, sympy.Pow):
                    chars.has_exponents = True
                if isinstance(factor, (sqrt, sympy.root)):
                    chars.has_radicals = True

        # Detect absolute value
        if expr.has(Abs):
            chars.has_absolute_value = True

        # Calculate polynomial degree
        if chars.has_equation and symbols:
            try:
                symbol = symbols[0]
                if isinstance(expr, Eq):
                    difference = expand(expr.lhs - expr.rhs)
                else:
                    difference = expand(expr)

                poly = Poly(difference, symbol)
                chars.max_polynomial_degree = poly.degree()
            except Exception:
                pass

    def _classify_problem_type(
        self, expr: Any, parsed: ParsedMath, chars: ProblemCharacteristics | None
    ) -> str:
        """Classify the main problem type."""

        # Priority 1: Calculus
        if isinstance(expr, Limit) or (
            isinstance(expr, Eq) and (isinstance(expr.rhs, Limit) or isinstance(expr.lhs, Limit))
        ):
            return "calculus_limit"

        if isinstance(expr, Derivative) or (
            isinstance(expr, Eq) and (isinstance(expr.rhs, Derivative) or isinstance(expr.lhs, Derivative))
        ):
            return "calculus_derivative"

        if isinstance(expr, Integral) or (
            isinstance(expr, Eq) and (isinstance(expr.rhs, Integral) or isinstance(expr.lhs, Integral))
        ):
            return "calculus_integral"

        # Priority 2: Inequalities
        if isinstance(
            expr, (sympy.StrictLessThan, sympy.LessThan, sympy.StrictGreaterThan, sympy.GreaterThan)
        ):
            return self._classify_inequality(expr, parsed)

        # Priority 3: Check if it's an equation
        if not parsed.is_equation:
            return self._classify_expression(expr, parsed, chars)

        # Priority 4: Equations
        return self._classify_equation(expr, parsed, chars)

    def _classify_inequality(self, expr: Relational, parsed: ParsedMath) -> str:
        """Classify inequality types."""
        if len(parsed.symbols) == 0:
            return "numeric_inequality"

        if len(parsed.symbols) > 1:
            return "multivariate_inequality"

        try:
            symbol = parsed.symbols[0]
            difference = expand(expr.lhs - expr.rhs)
            degree = Poly(difference, symbol).degree()

            if degree == 1:
                return "linear_inequality"
            elif degree == 2:
                return "quadratic_inequality"
            else:
                return "polynomial_inequality"
        except Exception:
            return "unknown_inequality"

    def _classify_expression(
        self, expr: Any, parsed: ParsedMath, chars: ProblemCharacteristics | None
    ) -> str:
        """Classify non-equation expressions."""

        # Check for specific expression types
        if chars:
            # Trigonometric expression
            if chars.has_trigonometry:
                return "trigonometric_expression"

            # Rational/fraction expression
            if chars.has_fractions and not chars.has_equation:
                if not parsed.symbols:
                    return "fraction_arithmetic"
                return "rational_expression"

        # Check if it's purely arithmetic or has variables
        if not parsed.symbols:
            return "arithmetic_expression"

        # Check for factorization form (product of terms)
        if self._is_factored_form(expr):
            return "factored_expression"

        return "algebraic_expression"

    def _classify_equation(
        self, expr: Eq, parsed: ParsedMath, chars: ProblemCharacteristics | None
    ) -> str:
        """Classify equation types."""

        if len(parsed.symbols) == 0:
            return "numeric_equation"

        # Check for function definition f(x) = ...
        if isinstance(expr.lhs, (sympy.Function, sympy.core.function.AppliedUndef)):
            return "calculus_derivative"

        # Check for multiple equations (system)
        # This would need to be detected earlier in parsing for true systems
        if len(parsed.symbols) > 1:
            return "multivariate_equation"

        symbol = parsed.symbols[0]

        # Special equation types
        if chars:
            if chars.has_trigonometry:
                return "trigonometric_equation"

            if chars.has_absolute_value:
                return "absolute_value_equation"

            if chars.has_radicals:
                return "radical_equation"

            if chars.has_complex_numbers:
                return "complex_equation"

        # Classify by polynomial degree
        try:
            difference = expand(expr.lhs - expr.rhs)
            degree = Poly(difference, symbol).degree()

            if degree == 1:
                return "linear_equation"
            elif degree == 2:
                return "quadratic_equation"
            elif degree > 2:
                return "polynomial_equation"
        except Exception:
            pass

        # Check for rational equations (fractions with variables)
        if chars and chars.has_fractions:
            return "rational_equation"

        return "unknown_equation"

    def _is_factored_form(self, expr: Any) -> bool:
        """Check if expression is in factored form (product of factors)."""
        try:
            if isinstance(expr, sympy.Mul):
                # Check if it has multiple non-trivial factors
                factors = expr.as_ordered_factors()
                non_trivial_factors = [
                    f for f in factors if not isinstance(f, (int, Float)) and f != 1
                ]
                return len(non_trivial_factors) >= 2
        except Exception:
            pass
        return False


# Singleton instance for backward compatibility
_classifier_instance: ProblemClassifier | None = None


def get_classifier() -> ProblemClassifier:
    """Get singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ProblemClassifier()
    return _classifier_instance


def classify_problem(parsed: ParsedMath) -> str:
    """
    Backward-compatible function for existing code.

    Classifies problem and returns only the problem_type string.
    """
    classifier = get_classifier()
    problem_type, _ = classifier.classify(parsed, detect_characteristics=False)
    return problem_type


def classify_with_characteristics(parsed: ParsedMath) -> tuple[str, ProblemCharacteristics]:
    """
    Enhanced classification that returns both type and characteristics.

    Returns:
        Tuple of (problem_type, characteristics)
    """
    classifier = get_classifier()
    problem_type, chars = classifier.classify(parsed, detect_characteristics=True)

    # Ensure characteristics is never None
    if chars is None:
        chars = ProblemCharacteristics()

    return problem_type, chars


# Map problem types to difficulty/complexity estimates
PROBLEM_TYPE_COMPLEXITY = {
    "arithmetic_expression": 1,
    "numeric_equation": 1,
    "fraction_arithmetic": 2,
    "linear_equation": 2,
    "linear_inequality": 2,
    "quadratic_equation": 3,
    "quadratic_inequality": 3,
    "polynomial_equation": 4,
    "polynomial_inequality": 4,
    "rational_expression": 4,
    "rational_equation": 5,
    "radical_equation": 5,
    "absolute_value_equation": 5,
    "trigonometric_expression": 5,
    "trigonometric_equation": 6,
    "multivariate_equation": 6,
    "calculus_limit": 7,
    "calculus_derivative": 7,
    "calculus_integral": 8,
    "complex_equation": 6,
    "unknown_equation": 5,
}


def get_problem_complexity(problem_type: str) -> int:
    """
    Get complexity estimate for a problem type (1-10 scale).

    This can be used for:
    - Ordering problems by difficulty
    - Selecting appropriate hint levels
    - Gamification/progression systems
    """
    return PROBLEM_TYPE_COMPLEXITY.get(problem_type, 5)
