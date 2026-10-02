"""
System of equations solver (placeholder for future implementation).
"""

from __future__ import annotations

from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class SystemSolver(BaseSolver):
    """
    Solves systems of linear equations (future implementation).

    Handles:
    - 2x2 systems: two equations, two unknowns
    - 3x3 systems: three equations, three unknowns
    - Larger systems

    Note: Currently not fully implemented. This is a placeholder for Phase 4.
    """

    SUPPORTED_TYPES = {
        "system_linear_2x2",
        "system_linear_3x3",
        "system_equations",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve a system of equations.

        Note: This is a placeholder. Full implementation requires:
        1. Parser support for multiple equations
        2. UI for inputting multiple equations
        3. Step generator for system solving methods (substitution, elimination)
        """
        return SolveResult(
            answer=None,
            variable=None,
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km="ប្រព័ន្ធសមីការ - មិនទាន់អនុវត្ត",
                    description_en="System of equations - not yet implemented",
                    expression="Coming in Phase 4",
                )
            ],
            metadata={
                "note": "System solving requires additional parser and UI work",
                "planned_for": "Phase 4",
            },
        )
