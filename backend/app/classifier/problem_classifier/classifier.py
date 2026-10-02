"""
Classify a ParsedMath object into a problem_type string. This string drives
both which step generator is used and what the API reports back in
`problem_type`, so keep the set of values stable — the mobile app may
eventually branch on it (e.g. to show a different icon per problem type).

This module now uses the enhanced classifier for improved detection while
maintaining backward compatibility with existing code.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Limit, Poly

from app.parser.math_parser.expression_parser import ParsedMath

# Import enhanced classifier
try:
    from app.classifier.problem_classifier.classifier_enhanced import (
        classify_problem as _classify_enhanced,
        classify_with_characteristics,
        get_problem_complexity,
    )

    _USE_ENHANCED = True
except ImportError:
    _USE_ENHANCED = False
    classify_with_characteristics = None
    get_problem_complexity = None


def classify_problem(parsed: ParsedMath) -> str:
    """
    Classify a parsed mathematical expression into a problem type.

    Uses enhanced classifier if available, falls back to legacy implementation.
    """
    # Use enhanced classifier if available
    if _USE_ENHANCED:
        return _classify_enhanced(parsed)

    # Legacy implementation (fallback)
    expr = parsed.sympy_expr

    # Check if it's an inequality (relational expression) - do this FIRST
    # before checking is_equation, since inequalities have is_equation=False
    if isinstance(
        expr, (sympy.StrictLessThan, sympy.LessThan, sympy.StrictGreaterThan, sympy.GreaterThan)
    ):
        if len(parsed.symbols) == 0:
            return "numeric_inequality"
        if len(parsed.symbols) > 1:
            return "multivariate_inequality"
        # Determine if it's linear or higher degree
        try:
            symbol = parsed.symbols[0]
            difference = sympy.expand(expr.lhs - expr.rhs)
            degree = Poly(difference, symbol).degree()
            if degree == 1:
                return "linear_inequality"
            elif degree == 2:
                return "quadratic_inequality"
            else:
                return "polynomial_inequality"
        except Exception:
            return "unknown_inequality"

    # Check if it's a calculus limit
    if isinstance(expr, Limit):
        return "calculus_limit"
    if isinstance(expr, Eq) and (isinstance(expr.rhs, Limit) or isinstance(expr.lhs, Limit)):
        return "calculus_limit"

    # Now check equations
    if not parsed.is_equation:
        return "algebraic_expression" if parsed.symbols else "arithmetic_expression"

    eq = parsed.sympy_expr  # a sympy.Eq

    if len(parsed.symbols) == 0:
        return "numeric_equation"  # e.g. "5 = 5" — a statement, not a solve

    if len(parsed.symbols) > 1:
        return "multivariate_equation"  # e.g. two-variable systems — future work

    symbol = parsed.symbols[0]
    try:
        difference = sympy.expand(eq.lhs - eq.rhs)
        degree = Poly(difference, symbol).degree()
    except Exception:
        return "unknown_equation"

    if degree == 1:
        return "linear_equation"
    if degree == 2:
        return "quadratic_equation"
    if degree > 2:
        return "polynomial_equation"
    return "unknown_equation"


# Re-export enhanced functions if available
__all__ = ["classify_problem"]
if _USE_ENHANCED:
    __all__.extend(["classify_with_characteristics", "get_problem_complexity"])
