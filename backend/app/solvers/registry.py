"""
Solver Registry - Maps problem types to solver instances.

This module maintains a registry of all available solvers and provides
a lookup function to find the appropriate solver for a given problem type.

The registry is automatically populated when solvers are imported.
Adding a new solver is easy:
1. Create a solver class that extends BaseSolver
2. Import it in this module
3. Add an instance to SOLVERS list

The registry will automatically route problems to the correct solver
based on the problem_type string from the classifier.
"""

from __future__ import annotations

from app.solvers.algebra import EquationSolver, InequalitySolver, SequenceSolver, SystemSolver
from app.solvers.base import BaseSolver, ExpressionEvaluator, StatementChecker
from app.solvers.calculus import DerivativeSolver, IntegralSolver, LimitSolver

# Registry of all available solvers
# Order matters: solvers are checked in order, first match wins
SOLVERS: list[BaseSolver] = [
    # Sequence solver
    SequenceSolver(),
    # Calculus solvers
    DerivativeSolver(),
    IntegralSolver(),
    LimitSolver(),
    # Algebra solvers
    EquationSolver(),
    InequalitySolver(),
    SystemSolver(),
    # Base solvers (catch-all)
    StatementChecker(),
    ExpressionEvaluator(),
]



def get_solver(problem_type: str) -> BaseSolver | None:
    """
    Find the appropriate solver for the given problem type.

    Args:
        problem_type: Problem type string from classifier
                     (e.g., "linear_equation", "calculus_limit")

    Returns:
        Solver instance that can handle this problem type, or None if no solver found

    Examples:
        >>> solver = get_solver("linear_equation")
        >>> solver
        <EquationSolver object>

        >>> solver = get_solver("calculus_limit")
        >>> solver
        <LimitSolver object>

        >>> solver = get_solver("unknown_type")
        >>> solver
        None
    """
    for solver in SOLVERS:
        if solver.can_solve(problem_type):
            return solver
    return None


def list_supported_types() -> dict[str, str]:
    """
    List all supported problem types and their solver classes.

    Useful for debugging and documentation.

    Returns:
        Dictionary mapping problem type to solver class name

    Example:
        >>> types = list_supported_types()
        >>> types["linear_equation"]
        'EquationSolver'
    """
    supported = {}
    for solver in SOLVERS:
        solver_name = solver.__class__.__name__
        # Get supported types from solver
        if hasattr(solver, "SUPPORTED_TYPES"):
            for prob_type in solver.SUPPORTED_TYPES:
                supported[prob_type] = solver_name
    return supported


def register_solver(solver: BaseSolver, priority: int = -1) -> None:
    """
    Dynamically register a new solver at runtime (for plugins/extensions).

    Args:
        solver: Solver instance to register
        priority: Position in registry (0 = highest priority, -1 = lowest priority/append)

    Example:
        >>> my_solver = CustomTrigSolver()
        >>> register_solver(my_solver, priority=0)  # Check this solver first
    """
    if priority == -1:
        SOLVERS.append(solver)
    else:
        SOLVERS.insert(priority, solver)
