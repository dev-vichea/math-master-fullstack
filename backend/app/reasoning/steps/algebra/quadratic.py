"""
Step-by-step derivation for quadratic equations (ax² + bx + c = 0).

The algorithm:
  1. Show the original equation.
  2. If not in standard form, rearrange to ax² + bx + c = 0.
  3. Identify coefficients a, b, and c.
  4. Calculate and display the discriminant (Δ = b² - 4ac).
  5. Apply the quadratic formula based on the discriminant:
     - Δ > 0: Two distinct real roots
     - Δ = 0: One repeated root
     - Δ < 0: No real roots (complex roots)
  6. Show the final solution(s).

Every arithmetic operation is done by SymPy, and the final value is
substituted back and checked by verification.verify_solution before it is
ever returned to the API layer — the steps shown here are a *description*
of a computation SymPy already did, not a separate, potentially-wrong,
free-form explanation.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Symbol, expand, nsimplify, sqrt

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
    return str(value)


class QuadraticStepGenerator(StepGenerator):
    problem_type = "quadratic_equation"

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
                expression=f"{lhs} = {rhs}",
            )
        )
        order += 1

        # Move everything to the left side to get standard form: ax² + bx + c = 0
        standard_lhs = expand(lhs - rhs)
        if standard_lhs != lhs or rhs != 0:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេងដើម្បីទទួលបានទម្រង់ស្តង់ដារ៖",
                    description_en="Move all terms to the left to get standard form:",
                    expression=f"{standard_lhs} = 0",
                )
            )
            order += 1

        # Extract coefficients: a, b, c from ax² + bx + c = 0
        a = standard_lhs.coeff(symbol, 2)
        b = standard_lhs.coeff(symbol, 1)
        c = standard_lhs.coeff(symbol, 0)

        steps.append(
            SolutionStep(
                order=order,
                description_km=f"កំណត់​មេគុណ៖ a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}",
                description_en=f"Identify coefficients: a = {_format_number(a)}, b = {_format_number(b)}, c = {_format_number(c)}",
                expression=None,
            )
        )
        order += 1

        # Calculate discriminant: Δ = b² - 4ac
        discriminant = nsimplify(b**2 - 4 * a * c)
        steps.append(
            SolutionStep(
                order=order,
                description_km="គណនា​ឌីស្ក្រីមីណង់ Δ = b² - 4ac:",
                description_en="Calculate discriminant Δ = b² - 4ac:",
                expression=f"Δ = ({_format_number(b)})² - 4({_format_number(a)})({_format_number(c)}) = {_format_number(discriminant)}",
            )
        )
        order += 1

        # Apply quadratic formula based on discriminant value
        if discriminant > 0:
            # Two distinct real roots
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ដោយសារ Δ > 0, មានដំណោះស្រាយពីរផ្សេងគ្នា។ ប្រើរូបមន្តក្វាដ្រាទិក៖",
                    description_en="Since Δ > 0, there are two distinct real solutions. Using the quadratic formula:",
                    expression=f"{symbol} = (-b ± √Δ) / (2a)",
                )
            )
            order += 1

            # Calculate both roots
            sqrt_discriminant = sqrt(discriminant)
            root1 = nsimplify((-b + sqrt_discriminant) / (2 * a))
            root2 = nsimplify((-b - sqrt_discriminant) / (2 * a))

            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ចម្លើយ៖ {symbol} = {_format_number(root1)} ឬ {symbol} = {_format_number(root2)}",
                    description_en=f"Answer: {symbol} = {_format_number(root1)} or {symbol} = {_format_number(root2)}",
                    expression=f"{symbol} = {_format_number(root1)}, {_format_number(root2)}",
                )
            )

        elif discriminant == 0:
            # One repeated root
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ដោយសារ Δ = 0, មានដំណោះស្រាយតែមួយ (ឫសស្រីឡើងវិញ)។ ប្រើរូបមន្តក្វាដ្រាទិក៖",
                    description_en="Since Δ = 0, there is one repeated solution. Using the quadratic formula:",
                    expression=f"{symbol} = -b / (2a)",
                )
            )
            order += 1

            root = nsimplify(-b / (2 * a))
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ចម្លើយ៖ {symbol} = {_format_number(root)}",
                    description_en=f"Answer: {symbol} = {_format_number(root)}",
                    expression=f"{symbol} = {_format_number(root)}",
                )
            )

        else:  # discriminant < 0
            # No real roots (complex roots)
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ដោយសារ Δ < 0, គ្មានដំណោះស្រាយជាលេខពិតទេ (មានតែដំណោះស្រាយស្មុគស្មាញ)។",
                    description_en="Since Δ < 0, there are no real solutions (only complex solutions).",
                    expression=None,
                )
            )
            order += 1

            # Still compute complex roots for completeness
            sqrt_neg_discriminant = sqrt(-discriminant)
            real_part = nsimplify(-b / (2 * a))
            imag_part = nsimplify(sqrt_neg_discriminant / (2 * a))

            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ចម្លើយស្មុគស្មាញ៖ {symbol} = {_format_number(real_part)} ± {_format_number(imag_part)}i",
                    description_en=f"Complex solutions: {symbol} = {_format_number(real_part)} ± {_format_number(imag_part)}i",
                    expression=f"{symbol} = {_format_number(real_part)} + {_format_number(imag_part)}i, {_format_number(real_part)} - {_format_number(imag_part)}i",
                )
            )

        return steps
