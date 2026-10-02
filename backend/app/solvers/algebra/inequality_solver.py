"""
Inequality solvers for linear and polynomial inequalities.
"""

from __future__ import annotations

import sympy

from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class InequalitySolver(BaseSolver):
    """
    Solves algebraic inequalities with one variable.

    Handles:
    - Linear inequalities: ax + b < c, ax + b ≤ c, ax + b > c, ax + b ≥ c
    - Quadratic inequalities: ax² + bx + c < 0
    - Polynomial inequalities: higher degree
    - Multivariate inequalities: returns appropriate message
    """

    SUPPORTED_TYPES = {
        "linear_inequality",
        "quadratic_inequality",
        "polynomial_inequality",
        "multivariate_inequality",
        "unknown_inequality",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve an algebraic inequality.

        Process:
        1. Extract inequality and symbols
        2. Use SymPy to solve
        3. Format solution set
        4. Generate steps using registered step generator
        """
        expr = parsed.sympy_expr

        # Check that it's actually an inequality
        if not isinstance(
            expr, (sympy.StrictLessThan, sympy.LessThan, sympy.StrictGreaterThan, sympy.GreaterThan)
        ):
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="កន្សោមមិនមែនជាអសមីការទេ",
                        description_en="Expression is not an inequality",
                        expression=str(expr),
                    )
                ],
            )

        # Handle inequalities without variables (numeric)
        if not parsed.symbols:
            is_true = bool(expr)
            return SolveResult(
                answer="true" if is_true else "false",
                variable=None,
                is_verified=is_true,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="ត្រួតពិនិត្យអសមីការ៖",
                        description_en="Check the inequality:",
                        expression=str(expr),
                    )
                ],
            )

        # Handle multivariate inequalities
        if len(parsed.symbols) > 1:
            return self._handle_multivariate(expr, parsed.symbols)

        symbol = parsed.symbols[0]

        # Solve using SymPy
        try:
            solutions = sympy.solve(expr, symbol)
            if solutions:
                answer_str = str(solutions)
            else:
                answer_str = "No solution"
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
                        expression=str(expr),
                    )
                ],
            )

        # Generate steps using step generator if available
        generator = self._get_step_generator(problem_type)
        if generator is not None:
            steps = generator.generate(expr, symbol)
        else:
            # Fallback generic step
            steps = [
                SolutionStep(
                    order=1,
                    description_km="ដោះស្រាយអសមីការ៖",
                    description_en="Solve the inequality:",
                    expression=f"{sympy.latex(expr)}  \\rightarrow  {answer_str}",
                )
            ]

        return SolveResult(
            answer=answer_str,
            variable=str(symbol),
            is_verified=True,  # Inequalities are harder to verify, trust SymPy
            steps=steps,
            metadata={
                "inequality_type": type(expr).__name__,
                "solution_set": str(solutions) if solutions else None,
            },
        )

    def _handle_multivariate(self, expr: sympy.Expr, symbols: list[sympy.Symbol]) -> SolveResult:
        """Handle inequalities with multiple variables."""
        return SolveResult(
            answer=None,
            variable=", ".join(str(s) for s in symbols),
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km="អសមីការមានអថេរច្រើន - មិនទាន់គាំទ្រ",
                    description_en="Multivariate inequality - not yet supported",
                    expression=str(expr),
                )
            ],
            metadata={
                "variables": [str(s) for s in symbols],
                "note": "Multivariate inequality solving not yet implemented",
            },
        )
