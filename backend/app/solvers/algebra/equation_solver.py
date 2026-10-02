"""
Equation solvers for linear, quadratic, and polynomial equations.
"""

from __future__ import annotations

import sympy
from sympy import Eq

from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class EquationSolver(BaseSolver):
    """
    Solves algebraic equations with one variable.

    Handles:
    - Linear equations: ax + b = c
    - Quadratic equations: ax² + bx + c = 0
    - Polynomial equations: degree > 2
    - Multivariate equations: returns appropriate message
    """

    SUPPORTED_TYPES = {
        "linear_equation",
        "quadratic_equation",
        "polynomial_equation",
        "multivariate_equation",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve an algebraic equation.

        Process:
        1. Extract equation and symbols
        2. Use SymPy to solve
        3. Verify the solution
        4. Generate steps using registered step generator
        """
        eq: Eq = parsed.sympy_expr

        # Handle multivariate equations
        if len(parsed.symbols) > 1:
            return self._handle_multivariate(eq, parsed.symbols)

        # Single variable equation
        if len(parsed.symbols) == 0:
            # This shouldn't happen (would be numeric_equation), but handle it
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="មិនមានអថេរក្នុងសមីការ",
                        description_en="No variable in equation",
                        expression=str(eq),
                    )
                ],
            )

        symbol = parsed.symbols[0]

        # Solve using SymPy
        try:
            solutions = sympy.solve(eq, symbol)
        except Exception as e:
            return SolveResult(
                answer=None,
                variable=str(symbol),
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km=f"មិនអាចដោះស្រាយបាន៖ {str(e)}",
                        description_en=f"Unable to solve: {str(e)}",
                        expression=str(eq),
                    )
                ],
            )

        if not solutions:
            return SolveResult(
                answer=None,
                variable=str(symbol),
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="គ្មានដំណោះស្រាយ",
                        description_en="No solution",
                        expression=str(eq),
                    )
                ],
            )

        # Verify the primary solution
        primary_solution = solutions[0]
        is_verified = self._verify_solution(eq, symbol, primary_solution)

        # Generate steps using step generator if available
        generator = self._get_step_generator(problem_type)
        if generator is not None:
            steps = generator.generate(eq, symbol)
        else:
            # Fallback generic step
            steps = [
                SolutionStep(
                    order=1,
                    description_km="ដោះស្រាយសមីការ៖",
                    description_en="Solve the equation:",
                    expression=f"{sympy.latex(eq)}  \\rightarrow  {symbol} = {', '.join(sympy.latex(s) for s in solutions)}",
                )
            ]

        # Format answer
        if len(solutions) > 1:
            answer = ", ".join(str(s) for s in solutions)
        else:
            answer = str(primary_solution)

        return SolveResult(
            answer=answer,
            variable=str(symbol),
            is_verified=is_verified,
            steps=steps,
            metadata={
                "solution_count": len(solutions),
                "all_solutions": [str(s) for s in solutions],
            },
        )

    def _handle_multivariate(self, eq: Eq, symbols: list[sympy.Symbol]) -> SolveResult:
        """Handle equations with multiple variables (currently not fully supported)."""
        return SolveResult(
            answer=None,
            variable=", ".join(str(s) for s in symbols),
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km="សមីការមានអថេរច្រើន - ត្រូវការសមីការបន្ថែម",
                    description_en="Multivariate equation - requires additional equations",
                    expression=str(eq),
                )
            ],
            metadata={
                "variables": [str(s) for s in symbols],
                "note": "System solving not yet implemented",
            },
        )
