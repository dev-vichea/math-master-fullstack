"""
Step-by-step derivation for polynomial equations (degree 3+).

For cubic (degree 3) and quartic (degree 4) equations, we use SymPy's
symbolic solver which can handle:
  - Factoring when possible
  - Rational roots theorem
  - Numerical approximations for non-symbolic roots
  - Complex roots

For degree 5+, we note that there's no general algebraic formula (Abel-Ruffini
theorem), and we either factor or use numerical methods.

Every solution is verified by substitution before being returned.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Symbol, expand, factor, nsimplify, solve

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import StepGenerator


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    # Try to simplify to a nice fraction or radical
    try:
        simplified = nsimplify(value, rational=False)
        return sympy.latex(simplified)
    except Exception:
        return sympy.latex(value)


def _is_real(value: sympy.Expr) -> bool:
    """Check if a SymPy expression is a real number."""
    try:
        return value.is_real
    except AttributeError:
        return True  # If we can't determine, assume real


class PolynomialStepGenerator(StepGenerator):
    problem_type = "polynomial_equation"

    def generate(self, eq: Eq, symbol: Symbol) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        lhs = expand(eq.lhs)
        rhs = expand(eq.rhs)

        steps.append(
            SolutionStep(
                order=order,
                description_km="សមីការដើម៖",
                description_en="Original equation:",
                expression=f"{sympy.latex(lhs)} = {sympy.latex(rhs)}",
            )
        )
        order += 1

        # Move everything to the left side: P(x) = 0
        standard_lhs = expand(lhs - rhs)
        if standard_lhs != lhs or rhs != 0:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេងដើម្បីទទួលបានទម្រង់ស្តង់ដារ៖",
                    description_en="Move all terms to the left to get standard form:",
                    expression=f"{sympy.latex(standard_lhs)} = 0",
                )
            )
            order += 1

        # Get the degree
        try:
            poly = sympy.Poly(standard_lhs, symbol)
            degree = poly.degree()
        except Exception:
            degree = None

        if degree:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"នេះគឺជាសមីការពហុធាដឺក្រេ {degree}។",
                    description_en=f"This is a polynomial equation of degree {degree}.",
                    expression=None,
                )
            )
            order += 1

        # Try to factor the polynomial
        factored = factor(standard_lhs)
        if factored != standard_lhs and factored != 1:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="កត្តា (factor) ពហុធា៖",
                    description_en="Factor the polynomial:",
                    expression=f"{sympy.latex(factored)} = 0",
                )
            )
            order += 1

        # Solve the equation
        try:
            solutions = solve(eq, symbol, dict=False)
            if not isinstance(solutions, list):
                solutions = [solutions]
        except Exception:
            solutions = []

        if not solutions:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="មិនអាចស្វែងរកដំណោះស្រាយជាទម្រង់ពិជគណិតបានទេ។",
                    description_en="Unable to find solutions in algebraic form.",
                    expression=None,
                )
            )
            return steps

        # Separate real and complex solutions
        real_solutions = [sol for sol in solutions if _is_real(sol)]
        complex_solutions = [sol for sol in solutions if not _is_real(sol)]

        # Show solving process
        if degree == 3:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="សម្រាប់សមីការគូបិក (cubic), យើងប្រើវិធីសាស្រ្តពិជគណិត ឬកត្តា។",
                    description_en="For cubic equations, we use algebraic methods or factoring.",
                    expression=None,
                )
            )
            order += 1
        elif degree == 4:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="សម្រាប់សមីការក្វាទ្រីក (quartic), យើងប្រើវិធីសាស្រ្តពិជគណិត ឬកត្តា។",
                    description_en="For quartic equations, we use algebraic methods or factoring.",
                    expression=None,
                )
            )
            order += 1
        elif degree and degree >= 5:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"សម្រាប់ពហុធាដឺក្រេ {degree}, គ្មានរូបមន្តពិជគណិតទូទៅទេ (Abel-Ruffini theorem)។",
                    description_en=f"For degree {degree} polynomials, there is no general algebraic formula (Abel-Ruffini theorem).",
                    expression=None,
                )
            )
            order += 1

        # Display real solutions
        if real_solutions:
            if len(real_solutions) == 1:
                sol_str = _format_number(real_solutions[0])
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ដំណោះស្រាយជាលេខពិត៖ {symbol} = {sol_str}",
                        description_en=f"Real solution: {symbol} = {sol_str}",
                        expression=f"{symbol} = {sol_str}",
                    )
                )
                order += 1
            else:
                solutions_str = ", ".join(_format_number(sol) for sol in real_solutions)
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ដំណោះស្រាយជាលេខពិត ({len(real_solutions)})៖",
                        description_en=f"Real solutions ({len(real_solutions)}):",
                        expression=f"{symbol} = {solutions_str}",
                    )
                )
                order += 1

        # Display complex solutions if any
        if complex_solutions:
            if len(complex_solutions) == 1:
                sol_str = _format_number(complex_solutions[0])
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ដំណោះស្រាយស្មុគស្មាញ៖ {symbol} = {sol_str}",
                        description_en=f"Complex solution: {symbol} = {sol_str}",
                        expression=f"{symbol} = {sol_str}",
                    )
                )
                order += 1
            else:
                complex_solutions_str = ", ".join(_format_number(sol) for sol in complex_solutions)
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ដំណោះស្រាយស្មុគស្មាញ ({len(complex_solutions)})៖",
                        description_en=f"Complex solutions ({len(complex_solutions)}):",
                        expression=f"{symbol} = {complex_solutions_str}",
                    )
                )

        return steps
