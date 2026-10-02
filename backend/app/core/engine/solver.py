"""
Orchestrates: ParsedMath + problem_type -> SolveResult.

DEPRECATED: This module has been moved to app/solvers/
Please update imports to use app.solvers instead.

The new modular architecture provides:
- Clean separation of concerns (algebra, calculus, etc.)
- Easier to add new solver types
- Better testability and maintainability
- Each solver is self-contained with its own logic

Migration guide:
    Old: from app.core.engine.solver import solve, SolveResult
    New: from app.solvers import solve, SolveResult
"""

from __future__ import annotations

import warnings

from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers import solve as _new_solve
from app.solvers.base import SolveResult

warnings.warn(
    "app.core.engine.solver is deprecated. Please use app.solvers instead.",
    DeprecationWarning,
    stacklevel=2,
)


def solve(parsed: ParsedMath, problem_type: str) -> SolveResult:
    """
    DEPRECATED: Use app.solvers.solve() instead.

    This function now delegates to the new modular solver architecture.
    """
    return _new_solve(parsed, problem_type)


__all__ = ["solve", "SolveResult"]
