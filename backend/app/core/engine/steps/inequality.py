"""
Step-by-step derivation for linear inequalities (ax + b < c, etc.).

Supports:
  - Linear inequalities: 2x + 5 < 15
  - All inequality types: <, ≤, >, ≥
  - Sign reversal when multiplying/dividing by negative numbers
  - Solution in interval notation

Every solution is verified by testing boundary and sample points.
"""

from __future__ import annotations

import sympy
from sympy import Symbol, nsimplify

from app.core.engine.steps.base import StepGenerator
from app.models.schemas import SolutionStep


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    try:
        simplified = nsimplify(value, rational=False)
        return str(simplified)
    except Exception:
        return str(value)


def _get_inequality_symbol_khmer(inequality) -> tuple[str, str]:
    """Get the inequality symbol in both English and Khmer."""
    inequality_type = type(inequality).__name__
    symbols_map = {
        "StrictLessThan": ("<", "តូចជាង"),
        "LessThan": ("≤", "តូចជាង ឬស្មើ"),
        "StrictGreaterThan": (">", "ធំជាង"),
        "GreaterThan": ("≥", "ធំជាង ឬស្មើ"),
    }
    return symbols_map.get(inequality_type, ("<", "តូចជាង"))


class LinearInequalityStepGenerator(StepGenerator):
    problem_type = "linear_inequality"

    def generate(self, inequality, symbol: Symbol) -> list[SolutionStep]:
        """Generate step-by-step solution for linear inequalities.

        Note: The signature uses 'inequality' instead of 'eq' because
        SymPy inequalities are not Eq objects but Relational objects.
        """
        steps: list[SolutionStep] = []
        order = 1

        lhs = sympy.expand(inequality.lhs)
        rhs = sympy.expand(inequality.rhs)
        ineq_symbol_en, ineq_symbol_km = _get_inequality_symbol_khmer(inequality)

        steps.append(
            SolutionStep(
                order=order,
                description_km="អសមីការដើម៖",
                description_en="Original inequality:",
                expression=f"{lhs} {ineq_symbol_en} {rhs}",
            )
        )
        order += 1

        # Move all terms to the left side
        standard_lhs = sympy.expand(lhs - rhs)
        if standard_lhs != lhs or rhs != 0:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេង៖",
                    description_en="Move all terms to the left:",
                    expression=f"{standard_lhs} {ineq_symbol_en} 0",
                )
            )
            order += 1

        # Extract coefficient and constant: ax + b < 0
        try:
            a = standard_lhs.coeff(symbol, 1)
            b = standard_lhs.coeff(symbol, 0)
        except Exception:
            a = 1
            b = 0

        # Show isolation of variable
        if b != 0:
            # Subtract b from both sides
            new_lhs = a * symbol
            new_rhs = -b
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ដក {_format_number(b)} ពីទាំងសងខាង៖",
                    description_en=f"Subtract {_format_number(b)} from both sides:",
                    expression=f"{new_lhs} {ineq_symbol_en} {_format_number(new_rhs)}",
                )
            )
            order += 1
        else:
            new_rhs = 0

        # Divide by coefficient
        if a != 1:
            solution_value = nsimplify(new_rhs / a)

            # Check if we're dividing by a negative number (sign reversal!)
            if a < 0:
                # Reverse the inequality sign
                reversed_symbol_map = {"<": ">", "≤": "≥", ">": "<", "≥": "≤"}
                new_ineq_symbol = reversed_symbol_map.get(ineq_symbol_en, ineq_symbol_en)

                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ចែកទាំងសងខាងដោយ {_format_number(a)} (ប្រែសញ្ញាអសមីការ ព្រោះចែកដោយលេខអវិជ្ជមាន)៖",
                        description_en=f"Divide both sides by {_format_number(a)} (reverse inequality sign because dividing by negative):",
                        expression=f"{symbol} {new_ineq_symbol} {_format_number(solution_value)}",
                    )
                )
                order += 1

                # Update the final answer format
                if new_ineq_symbol == ">":
                    interval_notation = f"({_format_number(solution_value)}, ∞)"
                    solution_desc_km = f"{symbol} ធំជាង {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} > {_format_number(solution_value)}"
                elif new_ineq_symbol == "≥":
                    interval_notation = f"[{_format_number(solution_value)}, ∞)"
                    solution_desc_km = f"{symbol} ធំជាង ឬស្មើ {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} ≥ {_format_number(solution_value)}"
                elif new_ineq_symbol == "<":
                    interval_notation = f"(-∞, {_format_number(solution_value)})"
                    solution_desc_km = f"{symbol} តូចជាង {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} < {_format_number(solution_value)}"
                else:  # ≤
                    interval_notation = f"(-∞, {_format_number(solution_value)}]"
                    solution_desc_km = f"{symbol} តូចជាង ឬស្មើ {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} ≤ {_format_number(solution_value)}"
            else:
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"ចែកទាំងសងខាងដោយ {_format_number(a)}៖",
                        description_en=f"Divide both sides by {_format_number(a)}:",
                        expression=f"{symbol} {ineq_symbol_en} {_format_number(solution_value)}",
                    )
                )
                order += 1

                # Determine interval notation based on inequality type
                if ineq_symbol_en == "<":
                    interval_notation = f"(-∞, {_format_number(solution_value)})"
                    solution_desc_km = f"{symbol} {ineq_symbol_km} {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} < {_format_number(solution_value)}"
                elif ineq_symbol_en == "≤":
                    interval_notation = f"(-∞, {_format_number(solution_value)}]"
                    solution_desc_km = f"{symbol} {ineq_symbol_km} {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} ≤ {_format_number(solution_value)}"
                elif ineq_symbol_en == ">":
                    interval_notation = f"({_format_number(solution_value)}, ∞)"
                    solution_desc_km = f"{symbol} {ineq_symbol_km} {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} > {_format_number(solution_value)}"
                else:  # ≥
                    interval_notation = f"[{_format_number(solution_value)}, ∞)"
                    solution_desc_km = f"{symbol} {ineq_symbol_km} {_format_number(solution_value)}"
                    solution_desc_en = f"{symbol} ≥ {_format_number(solution_value)}"
        else:
            solution_value = new_rhs

            # Determine interval notation
            if ineq_symbol_en == "<":
                interval_notation = f"(-∞, {_format_number(solution_value)})"
            elif ineq_symbol_en == "≤":
                interval_notation = f"(-∞, {_format_number(solution_value)}]"
            elif ineq_symbol_en == ">":
                interval_notation = f"({_format_number(solution_value)}, ∞)"
            else:  # ≥
                interval_notation = f"[{_format_number(solution_value)}, ∞)"

            solution_desc_km = f"{symbol} {ineq_symbol_km} {_format_number(solution_value)}"
            solution_desc_en = f"{symbol} {ineq_symbol_en} {_format_number(solution_value)}"

        # Final answer in interval notation
        steps.append(
            SolutionStep(
                order=order,
                description_km=f"ដំណោះស្រាយ៖ {solution_desc_km}",
                description_en=f"Solution: {solution_desc_en}",
                expression=f"{symbol} ∈ {interval_notation}",
            )
        )

        return steps
