"""
Deterministic verification: never trust a solution (whether it came from
SymPy or, eventually, from an AI model) without substituting it back into
the original equation and checking the two sides are actually equal.

DEPRECATED: This module is kept for backward compatibility.
New code should use app.core.verification.verifier instead.
"""

from __future__ import annotations

import sympy
from sympy import Eq


def verify_solution(eq: Eq, symbol: sympy.Symbol, candidate: sympy.Expr) -> bool:
    """
    Legacy verification function for backward compatibility.

    Returns boolean only. For enhanced verification with confidence scoring
    and detailed results, use app.core.verification.verifier.verify() instead.
    """
    try:
        lhs_value = eq.lhs.subs(symbol, candidate)
        rhs_value = eq.rhs.subs(symbol, candidate)
        return bool(sympy.simplify(lhs_value - rhs_value) == 0)
    except Exception:
        return False
