"""
Step-by-step derivation for linear equations (ax + b = cx + d).

Enhanced version with operation metadata tracking for better explainability.

The algorithm:
  1. Show the original equation.
  2. If the variable appears on both sides, collect it on the left.
  3. Move the remaining constant off the variable's side (add/subtract).
  4. Clear the coefficient (divide, or multiply by the reciprocal when the
     coefficient is itself a fraction — the way a textbook would phrase it).
  5. State the answer.

Every arithmetic operation is done by SymPy, and the final value is
substituted back and checked by verification.verify_solution before it is
ever returned to the API layer — the steps shown here are a *description*
of a computation SymPy already did, not a separate, potentially-wrong,
free-form explanation.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Symbol, expand, nsimplify

from app.api.schemas.responses import SolutionStep
from app.reasoning.operations import OperationType
from app.reasoning.steps.base import CalculationBuilder, StepGenerator, create_solution_step


def _to_latex(val: Any) -> str:
    if isinstance(val, (sympy.Expr, sympy.Symbol, sympy.Integer, sympy.Rational)):
        return sympy.latex(val)
    return str(val)


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    return sympy.latex(value)


class LinearStepGenerator(StepGenerator):
    problem_type = "linear_equation"

    def generate(self, eq: Eq, symbol: Symbol) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        lhs = expand(eq.lhs)
        rhs = expand(eq.rhs)

        # Step 1: Initial state
        calc_init = CalculationBuilder(f"{_to_latex(lhs)} = {_to_latex(rhs)}")
        steps.append(
            create_solution_step(
                order=order,
                title_km="កំណត់សមីការដើម",
                title_en="Original Equation",
                description_km="សមីការដើម៖",
                description_en="Original equation:",
                calc=calc_init,
                teacher_note=f"ដើម្បីដោះស្រាយសមីការដឺក្រេទី ១ មានមួយអថេរ គោលដៅគឺត្រូវរកតម្លៃ {symbol} ដោយទុកតួដែលមាន {symbol} នៅអង្គម្ខាង និងចំនួនថេរនៅអង្គម្ខាងទៀត។",
                operation=OperationType.INITIAL_STATE.value,
            )
        )
        order += 1

        lhs_coeff = lhs.coeff(symbol, 1)
        lhs_const = lhs - lhs_coeff * symbol
        rhs_coeff = rhs.coeff(symbol, 1)
        rhs_const = rhs - rhs_coeff * symbol

        # Step: collect all variable terms on the left, if needed.
        if rhs_coeff != 0:
            new_lhs_coeff = lhs_coeff - rhs_coeff
            new_lhs_expr = new_lhs_coeff * symbol + lhs_const
            new_rhs = rhs_const

            calc_var = CalculationBuilder()
            start_expr = (
                f"{lhs_coeff * symbol} + {_format_number(lhs_const)} = {rhs_coeff * symbol} + {rhs_const}"
                if rhs_const != 0
                else f"{lhs_coeff * symbol} + {_format_number(lhs_const)} = {rhs_coeff * symbol}"
            )
            calc_var.add_initial(start_expr)
            calc_var.add_step(
                f"ដក {_format_number(rhs_coeff * symbol)} ពីអង្គសងខាង",
                f"{lhs_coeff * symbol} - {_format_number(rhs_coeff * symbol)} + {_format_number(lhs_const)} = {rhs_const}",
            )
            calc_var.add_step("សម្រួលតួអថេរ", f"{new_lhs_expr} = {new_rhs}")

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ប្រមូលតួអថេរមកអង្គខាងឆ្វេង",
                    title_en="Collect Variable Terms on Left",
                    description_km=f"ផ្លាស់ទី {symbol} ទាំងអស់មកខាងឆ្វេង៖",
                    description_en=f"Move all {symbol} terms to the left side:",
                    calc=calc_var,
                    teacher_note=f"ប្រមូលតួដែលមានអថេរ {symbol} ទាំងអស់មកអង្គខាងឆ្វេង ដោយដក {_format_number(rhs_coeff * symbol)} ពីអង្គសងខាងនៃសមីការ៖",
                    operation=OperationType.MOVE_TERM.value,
                    operands=[str(symbol), str(rhs_coeff * symbol)],
                    equation_side="left",
                )
            )
            order += 1
            lhs_coeff = new_lhs_coeff
            rhs = new_rhs
        else:
            rhs = rhs_const

        # Step: move the remaining constant off the variable's side.
        if lhs_const != 0:
            new_rhs = rhs - lhs_const
            calc_const = CalculationBuilder()
            calc_const.add_initial(
                f"{lhs_coeff * symbol} {'+' if lhs_const > 0 else '-'} {_format_number(abs(lhs_const))} = {rhs}"
            )

            if lhs_const > 0:
                teacher_op = f"ដក {_format_number(lhs_const)}"
                calc_const.add_step(
                    f"បោះ {_format_number(lhs_const)} ទៅអង្គខាងស្តាំ (ដក {_format_number(lhs_const)})",
                    f"{lhs_coeff * symbol} = {rhs} - {_format_number(lhs_const)}",
                )
                calc_const.add_step("គណនាផលដក", f"{lhs_coeff * symbol} = {new_rhs}")
                op = OperationType.SUBTRACT
            else:
                teacher_op = f"បូក {_format_number(-lhs_const)}"
                calc_const.add_step(
                    f"បោះ {_format_number(abs(lhs_const))} ទៅអង្គខាងស្តាំ (បូក {_format_number(abs(lhs_const))})",
                    f"{lhs_coeff * symbol} = {rhs} + {_format_number(abs(lhs_const))}",
                )
                calc_const.add_step("គណនាផលបូក", f"{lhs_coeff * symbol} = {new_rhs}")
                op = OperationType.ADD

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="បោះចំនួនថេរទៅអង្គខាងស្តាំ",
                    title_en="Move Constant to Right",
                    description_km=f"{teacher_op} ពីភាគីទាំងពីរ៖",
                    description_en=f"{'Subtract' if lhs_const > 0 else 'Add'} {_format_number(abs(lhs_const))} from both sides:",
                    calc=calc_const,
                    teacher_note=f"ផ្ទេរចំនួនថេរ {_format_number(abs(lhs_const))} ទៅអង្គខាងស្តាំ ({teacher_op} លើអង្គទាំងសងខាង)៖",
                    important_note="ចំណាំ៖ ពេលប្តូរតួពីអង្គម្ខាងទៅអង្គម្ខាងទៀត ត្រូវប្តូរសញ្ញា (+ ទៅជា -, - ទៅជា +)!",
                    operation=op.value,
                    operands=[_format_number(abs(lhs_const))],
                    equation_side="both",
                )
            )
            order += 1
            rhs = new_rhs

        # Step: clear the coefficient of the variable.
        if lhs_coeff != 1:
            calc_div = CalculationBuilder()
            calc_div.add_initial(f"{_to_latex(lhs_coeff * symbol)} = {_to_latex(rhs)}")
            is_proper_fraction = lhs_coeff.is_Rational and lhs_coeff.q != 1

            if is_proper_fraction:
                reciprocal = nsimplify(1 / lhs_coeff)
                final_value = nsimplify(rhs * reciprocal)
                calc_div.add_step(
                    f"គុណអង្គសងខាងដោយចម្រាស {_format_number(reciprocal)}",
                    f"{symbol} = {_to_latex(rhs)} \\times {_format_number(reciprocal)}",
                )
                calc_div.add_step("គណនាតម្លៃចុងក្រោយ", f"{symbol} = {_format_number(final_value)}")
                op = OperationType.MULTIPLY
                val_operand = _format_number(reciprocal)
                desc_km = f"គុណភាគីទាំងពីរដោយ {_format_number(reciprocal)}៖"
                desc_en = f"Multiply both sides by {_format_number(reciprocal)}:"
                teacher_note = f"ដោយសារមេគុណជាប្រភាគ {_format_number(lhs_coeff)} គុណអង្គសងខាងដោយចម្រាសរបស់វាគឺ {_format_number(reciprocal)}៖"
            else:
                final_value = nsimplify(rhs / lhs_coeff)
                calc_div.add_step(
                    f"ចែកអង្គសងខាងដោយ {_format_number(lhs_coeff)}",
                    f"{symbol} = \\frac{{{_to_latex(rhs)}}}{{{_format_number(lhs_coeff)}}}",
                )
                calc_div.add_step("សម្រួលតម្លៃអថេរ", f"{symbol} = {_format_number(final_value)}")
                op = OperationType.DIVIDE
                val_operand = _format_number(lhs_coeff)
                desc_km = f"ចែកភាគីទាំងពីរដោយ {_format_number(lhs_coeff)}៖"
                desc_en = f"Divide both sides by {_format_number(lhs_coeff)}:"
                teacher_note = f"អង្គខាងឆ្វេងនៅសល់ {lhs_coeff}{symbol} = {rhs}។ ដើម្បីរក {symbol} ចែកអង្គសងខាងដោយ {_format_number(lhs_coeff)}៖"

            steps.append(
                create_solution_step(
                    order=order,
                    title_km="ចែកនឹងមេគុណដើម្បីរកតម្លៃអថេរ",
                    title_en="Isolate Variable",
                    description_km=desc_km,
                    description_en=desc_en,
                    calc=calc_div,
                    teacher_note=teacher_note,
                    operation=op.value,
                    operands=[val_operand],
                    equation_side="both",
                )
            )
            order += 1
        else:
            final_value = rhs

        # Final step
        calc_final = CalculationBuilder(f"{symbol} = {_format_number(final_value)}")
        steps.append(
            create_solution_step(
                order=order,
                title_km="ចម្លើយចុងក្រោយ",
                title_en="Final Answer",
                description_km=f"ចម្លើយ៖ {symbol} = {_format_number(final_value)}",
                description_en=f"Answer: {symbol} = {_format_number(final_value)}",
                calc=calc_final,
                teacher_note=f"ទទួលបានតម្លៃ {symbol} = {_format_number(final_value)}។ អាចយកតម្លៃនេះទៅជំនួសផ្ទៀងផ្ទាត់ក្នុងសមីការដើម។",
                operation=OperationType.FINAL_ANSWER.value,
            )
        )

        return steps
