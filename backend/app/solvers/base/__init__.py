"""
Base Solver Interfaces - Abstract classes and common types.

Defines the contract that all solvers must implement.
"""

from app.solvers.base.solver import BaseSolver, ExpressionEvaluator, StatementChecker
from app.solvers.base.types import SolveResult

__all__ = [
    "BaseSolver",
    "SolveResult",
    "ExpressionEvaluator",
    "StatementChecker",
]
