"""
Step-by-step derivation for Calculus Limits (e.g. lim_{x->c} f(x)).

Designed for High School Grade 12 / Cambodian BacII National Examination:
1. Identify original limit expression and target approach value x -> c.
2. Direct substitution test:
   - Evaluates numerator and denominator at x = c.
   - Detects indeterminate form 0/0 or oo/oo vs continuous direct evaluation.
3. Elimination of indeterminate form (លុបរាងមិនកំណត់):
   - Polynomial/rational: Factor numerator and denominator; cancel (x - c).
   - Trigonometric: Apply identities (e.g. 1 - cos^2 x = sin^2 x, cos 2x, etc.) and simplify.
   - Radical/roots: Multiply numerator and denominator by conjugate.
4. Final limit evaluation:
   - Substitute x = c into the reduced continuous expression to obtain the exact symbolic answer.
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Limit, S, Symbol, factor, latex, oo, trigsimp

from app.core.engine.steps.base import StepGenerator
from app.models.schemas import SolutionStep


def _format_pt_str(pt: Any) -> str:
    if pt == oo:
        return r"\infty"
    if pt == -oo:
        return r"-\infty"
    return str(pt)


class LimitStepGenerator(StepGenerator):
    problem_type = "calculus_limit"

    def generate(self, expr: Any, symbol: Symbol | None = None) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        if not isinstance(expr, Limit):
            return [
                SolutionStep(
                    order=1,
                    description_km="គណនាលីមីត៖",
                    description_en="Evaluate the limit:",
                    expression=str(expr),
                )
            ]

        f = expr.args[0]
        var = expr.args[1] if len(expr.args) > 1 else (symbol or Symbol("x"))
        pt = expr.args[2] if len(expr.args) > 2 else S.Zero

        pt_str = _format_pt_str(pt)

        # Step 1: Original Limit
        orig_latex = f"\\lim_{{{var} \\to {pt_str}}} \\left({latex(f)}\\right)"
        steps.append(
            SolutionStep(
                order=order,
                description_km="កំណត់កន្សោមលីមីតដើម៖",
                description_en="Given limit expression:",
                expression=orig_latex,
            )
        )
        order += 1

        # Direct substitution check
        num, den = f.as_numer_denom()

        is_indeterminate_0_0 = False
        is_indeterminate_oo_oo = False
        direct_eval_success = False
        direct_val = None

        if pt not in (oo, -oo):
            try:
                num_val = num.subs(var, pt)
                den_val = den.subs(var, pt)
                if num_val == 0 and den_val == 0:
                    is_indeterminate_0_0 = True
                elif den_val != 0:
                    direct_val = num_val / den_val
                    direct_eval_success = True
            except Exception:
                pass
        else:
            is_indeterminate_oo_oo = True

        # Step 2: Test Direct Substitution / Indeterminate Form
        if is_indeterminate_0_0:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ជំនួសតម្លៃ ${var} = {pt_str}$ ដោយផ្ទាល់ នាំឱ្យមានរាងមិនកំណត់ $\\frac{{0}}{{0}}$៖",
                    description_en=f"Direct substitution of ${var} = {pt_str}$ yields indeterminate form $\\frac{{0}}{{0}}$:",
                    expression=f"\\frac{{{latex(num)}}}{{{latex(den)}}} \\xrightarrow{{{var} = {pt_str}}} \\frac{{0}}{{0}} \\quad \\text{{(រាងមិនកំណត់)}}",
                )
            )
            order += 1
        elif is_indeterminate_oo_oo:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"នៅពេល ${var} \\to {pt_str}$ កន្សោមមានរាងមិនកំណត់ $\\frac{{\\infty}}{{\\infty}}$៖",
                    description_en=f"As ${var} \\to {pt_str}$, expression has indeterminate form $\\frac{{\\infty}}{{\\infty}}$:",
                    expression=r"\frac{\infty}{\infty} \quad \text{(រាងមិនកំណត់)}",
                )
            )
            order += 1
        elif direct_eval_success and direct_val is not None:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ជំនួសតម្លៃ ${var} = {pt_str}$ ដោយផ្ទាល់ (អនុគមន៍ជាប់ត្រង់ ${var} = {pt_str}$)៖",
                    description_en=f"Direct substitution of ${var} = {pt_str}$ (function is continuous at ${var} = {pt_str}$):",
                    expression=f"f({pt_str}) = \\frac{{{latex(num.subs(var, pt))}}}{{{latex(den.subs(var, pt))}}} = {latex(direct_val)}",
                )
            )
            order += 1

        # Step 3: Transformation / Factoring / Identity
        reduced_expr = None
        if is_indeterminate_0_0:
            # Check if trigonometric
            has_trig = any(f.has(func) for func in (sympy.sin, sympy.cos, sympy.tan))
            if has_trig:
                simplified_f = trigsimp(f)
                if simplified_f != f:
                    reduced_expr = simplified_f
                    steps.append(
                        SolutionStep(
                            order=order,
                            description_km="ប្រើរូបមន្តត្រីកោណមាត្រ និងសម្រួលកត្តារួមដើម្បីលុបរាងមិនកំណត់៖",
                            description_en="Apply trigonometric identities and cancel common factors to eliminate indeterminate form:",
                            expression=f"{latex(f)} = {latex(simplified_f)}",
                        )
                    )
                    order += 1
                else:
                    factored_den = factor(den)
                    if factored_den != den:
                        steps.append(
                            SolutionStep(
                                order=order,
                                description_km="បំបែកភាគបែងតាមរូបមន្តត្រីកោណមាត្រ៖",
                                description_en="Factor denominator using trigonometric identities:",
                                expression=f"{latex(den)} = {latex(factored_den)}",
                            )
                        )
                        order += 1
            else:
                # Algebraic rational function
                factored_num = factor(num)
                factored_den = factor(den)
                canceled_f = factor(f)

                if canceled_f != f:
                    reduced_expr = canceled_f
                    steps.append(
                        SolutionStep(
                            order=order,
                            description_km=f"ដាក់ភាគយក និងភាគបែងជាផលគុណកត្តា រួចសម្រួលកត្តារួម $({var} - {pt_str})$៖",
                            description_en=f"Factor numerator and denominator, then cancel the common factor $({var} - {pt_str})$:",
                            expression=f"\\frac{{{latex(factored_num)}}}{{{latex(factored_den)}}} = {latex(canceled_f)} \\quad (\\text{{ចំពោះ }} {var} \\neq {pt_str})",
                        )
                    )
                    order += 1
                elif factored_num != num or factored_den != den:
                    steps.append(
                        SolutionStep(
                            order=order,
                            description_km="ដាក់ភាគយក និងភាគបែងជាផលគុណកត្តា៖",
                            description_en="Factor numerator and denominator:",
                            expression=f"\\frac{{{latex(factored_num)}}}{{{latex(factored_den)}}}",
                        )
                    )
                    order += 1

        # Step 4: Final Limit Value
        final_val = expr.doit()
        eval_expr_latex = latex(reduced_expr) if reduced_expr is not None else latex(f)
        steps.append(
            SolutionStep(
                order=order,
                description_km=f"គណនាតម្លៃលីមីតចុងក្រោយនៅពេល ${var} \\to {pt_str}$៖",
                description_en=f"Evaluate the final limit as ${var} \\to {pt_str}$:",
                expression=f"\\lim_{{{var} \\to {pt_str}}} \\left({eval_expr_latex}\\right) = {latex(final_val)}",
            )
        )

        return steps
