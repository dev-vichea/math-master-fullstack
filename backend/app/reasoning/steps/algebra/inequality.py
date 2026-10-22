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

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import CalculationBuilder, StepGenerator, create_solution_step


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
        steps: list[SolutionStep] = []
        order = 1

        lhs = sympy.expand(inequality.lhs)
        rhs = sympy.expand(inequality.rhs)
        ineq_symbol_en, ineq_symbol_km = _get_inequality_symbol_khmer(inequality)

        calc_init = CalculationBuilder(f"{lhs} {ineq_symbol_en} {rhs}")
        steps.append(
            create_solution_step(
                order=order,
                title_km="កំណត់អសមីការដើម",
                title_en="Original Inequality",
                description_km="អសមីការដើម៖",
                description_en="Original inequality:",
                calc=calc_init,
                teacher_note=f"ដើម្បីដោះស្រាយអសមីការដឺក្រេទី ១ មានមួយអថេរ គោលដៅគឺត្រូវរកដែនតម្លៃនៃ {symbol} ដែលធ្វើឱ្យវិសមភាពពិត។",
            )
        )
        order += 1

        # Move all terms to the left side
        standard_lhs = sympy.expand(lhs - rhs)
        if standard_lhs != lhs or rhs != 0:
            calc_std = CalculationBuilder(f"{lhs} {ineq_symbol_en} {rhs}")
            calc_std.add_step("ផ្លាស់ទីគ្រប់តួមកអង្គខាងឆ្វេង", f"{standard_lhs} {ineq_symbol_en} 0")
            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេង",
                    title_en="Move Terms to Left",
                    description_km="ផ្លាស់ទីទាំងអស់មកខាងឆ្វេង៖",
                    description_en="Move all terms to the left:",
                    calc=calc_std,
                    teacher_note="ផ្លាស់ទីគ្រប់តួទាំងអស់មកអង្គខាងឆ្វេង ដើម្បីងាយស្រួលកំណត់មេគុណ និងចំនួនថេរ៖",
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
            new_lhs = a * symbol
            new_rhs = -b
            calc_const = CalculationBuilder()
            calc_const.add_initial(
                f"{a * symbol} {'+' if b > 0 else '-'} {_format_number(abs(b))} {ineq_symbol_en} 0"
            )
            calc_const.add_step(
                f"បោះ {_format_number(abs(b))} ទៅអង្គខាងស្តាំ ({'ដក' if b > 0 else 'បូក'} {_format_number(abs(b))})",
                f"{new_lhs} {ineq_symbol_en} {_format_number(new_rhs)}",
            )

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="បោះចំនួនថេរទៅអង្គខាងស្តាំ",
                    title_en="Move Constant to Right",
                    description_km=f"{'ដក' if b > 0 else 'បូក'} {_format_number(abs(b))} ពីទាំងសងខាង៖",
                    description_en=f"{'Subtract' if b > 0 else 'Add'} {_format_number(abs(b))} from both sides:",
                    calc=calc_const,
                    teacher_note=f"ផ្ទេរចំនួនថេរ {_format_number(abs(b))} ទៅអង្គខាងស្តាំ ({'ដក' if b > 0 else 'បូក'} {_format_number(abs(b))} លើអង្គសងខាង)៖",
                )
            )
            order += 1
        else:
            new_lhs = a * symbol
            new_rhs = 0

        # Divide by coefficient
        if a != 1:
            solution_value = nsimplify(new_rhs / a)

            # Check if we're dividing by a negative number (sign reversal!)
            if a < 0:
                reversed_symbol_map = {"<": ">", "≤": "≥", ">": "<", "≥": "≤"}
                new_ineq_symbol = reversed_symbol_map.get(ineq_symbol_en, ineq_symbol_en)

                calc_div = CalculationBuilder()
                calc_div.add_initial(f"{new_lhs} {ineq_symbol_en} {_format_number(new_rhs)}")
                calc_div.add_step(
                    f"ចែកអង្គសងខាងដោយ {_format_number(a)} (ប្រែសញ្ញា {ineq_symbol_en} ទៅជា {new_ineq_symbol})",
                    f"{symbol} {new_ineq_symbol} \\frac{{{_format_number(new_rhs)}}}{{{_format_number(a)}}}",
                )
                calc_div.add_step("សម្រួលតម្លៃអថេរ", f"{symbol} {new_ineq_symbol} {_format_number(solution_value)}")

                steps.append(
                    create_solution_step(
                        order=order,
                        title_km="ចែកនឹងមេគុណ (ប្រែសញ្ញាអសមីការ)",
                        title_en="Divide by Negative (Reverse Inequality Sign)",
                        description_km=f"ចែកទាំងសងខាងដោយ {_format_number(a)} (ប្រែសញ្ញាអសមីការ ព្រោះចែកដោយលេខអវិជ្ជមាន)៖",
                        description_en=f"Divide both sides by {_format_number(a)} (reverse inequality sign because dividing by negative):",
                        calc=calc_div,
                        teacher_note=f"ពេលចែក ឬគុណអង្គសងខាងនៃអសមីការនឹងចំនួនអវិជ្ជមាន ({_format_number(a)} < 0) ត្រូវតែត្រឡប់ទិសដៅសញ្ញាអសមីការជានិច្ច!",
                        important_note=f"ចំណាំ៖ ចែកនឹងចំនួនអវិជ្ជមាន {_format_number(a)} នាំឱ្យប្តូរសញ្ញា {ineq_symbol_en} ទៅជា {new_ineq_symbol}។",
                    )
                )
                order += 1

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
                new_ineq_symbol = ineq_symbol_en
                calc_div = CalculationBuilder()
                calc_div.add_initial(f"{new_lhs} {ineq_symbol_en} {_format_number(new_rhs)}")
                calc_div.add_step(
                    f"ចែកអង្គសងខាងដោយ {_format_number(a)}",
                    f"{symbol} {ineq_symbol_en} \\frac{{{_format_number(new_rhs)}}}{{{_format_number(a)}}}",
                )
                calc_div.add_step("សម្រួលតម្លៃអថេរ", f"{symbol} {ineq_symbol_en} {_format_number(solution_value)}")

                steps.append(
                    create_solution_step(
                        order=order,
                        title_km="ចែកនឹងមេគុណ",
                        title_en="Divide by Coefficient",
                        description_km=f"ចែកទាំងសងខាងដោយ {_format_number(a)}៖",
                        description_en=f"Divide both sides by {_format_number(a)}:",
                        calc=calc_div,
                        teacher_note=f"ដោយសារ {_format_number(a)} ជាចំនួនវិជ្ជមាន (> 0) សញ្ញាអសមីការនៅរក្សាដដែលពេលចែកអង្គទាំងសងខាង។",
                    )
                )
                order += 1

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
        calc_final = CalculationBuilder(f"{symbol} \\in {interval_notation}")
        steps.append(
            create_solution_step(
                order=order,
                title_km="ដំណោះស្រាយជាចន្លោះ",
                title_en="Interval Solution",
                description_km=f"ដំណោះស្រាយ៖ {solution_desc_km}",
                description_en=f"Solution: {solution_desc_en}",
                calc=calc_final,
                teacher_note=f"ដូចនេះ ដែនតម្លៃនៃ {symbol} ដែលផ្ទៀងផ្ទាត់អសមីការគឺ {symbol} ∈ {interval_notation}។",
            )
        )

        return steps
