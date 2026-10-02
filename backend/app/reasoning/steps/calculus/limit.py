"""
Step-by-step derivation for Calculus Limits (e.g. lim_{x->c} f(x)).

Designed for High School Grade 12 / Cambodian BacII National Examination:
1. Identify original limit expression and target approach value x -> c.
2. Direct substitution test:
   - Evaluates numerator and denominator at x = c.
   - Detects indeterminate form 0/0 or oo/oo vs continuous direct evaluation.
3. Elimination of indeterminate form (លុបរាងមិនកំណត់):
   - Polynomial/rational: Factor numerator and denominator; cancel (x - c).
   - Radical/roots: Multiply numerator and denominator by conjugate.
   - Trigonometric: Apply identities and simplify.
4. Final limit evaluation:
   - Substitute x = c into the reduced continuous expression to obtain the exact symbolic answer.
5. Verification (if given an equation or target value):
   - Compares evaluated limit with right-hand side.
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Limit, S, Symbol, factor, latex, oo, trigsimp

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import StepGenerator


def _format_pt_str(pt: Any) -> str:
    if pt == oo:
        return r"\infty"
    if pt == -oo:
        return r"-\infty"
    return str(pt)


def _to_latex(expr_or_str: Any) -> str:
    """Convert expression to LaTeX string with standard Khmer \ln notation."""
    if isinstance(expr_or_str, str):
        s = expr_or_str
    else:
        s = latex(expr_or_str)
    return s.replace(r"\log", r"\ln")


def simplify_real_roots(expr: Any) -> Any:
    """In real calculus, simplify (-1)**(p/q) for odd q to (-1)**p."""
    if not hasattr(expr, "replace"):
        return expr

    def replace_neg_powers(e: Any) -> Any:
        if isinstance(e, sympy.Pow):
            base, exp = e.as_base_exp()
            if base == -1 and exp.is_Rational and exp.q % 2 == 1:
                return (-1) ** exp.p
        return e

    try:
        return expr.replace(lambda e: isinstance(e, sympy.Pow) and e.base == -1, replace_neg_powers)
    except Exception:
        return expr


def detect_limit_method(expr: Limit) -> str:
    """Determine the curriculum method ID for a given limit."""
    if not isinstance(expr, Limit):
        return "method_limit_direct_substitution"

    f = expr.args[0]
    var = expr.args[1] if len(expr.args) > 1 else Symbol("x")
    pt = expr.args[2] if len(expr.args) > 2 else S.Zero

    # Logarithmic limits (Grade 12 Chapter 4 Lesson 2)
    if f.has(sympy.log):
        if pt in (oo, -oo):
            return "method_limit_logarithm_infinity"
        elif pt == 0:
            return "method_limit_logarithm_zero"

    if pt in (oo, -oo):
        return "method_limit_factor_cancel"

    num, den = f.as_numer_denom()
    try:
        num_val = num.subs(var, pt)
        den_val = den.subs(var, pt)
        if num_val == 0 and den_val == 0:
            has_radical = any(
                isinstance(p, sympy.Pow) and p.exp.is_Rational and p.exp.q != 1
                for p in f.atoms(sympy.Pow)
            )
            if has_radical:
                return "method_limit_conjugate"
            return "method_limit_factor_cancel"
        elif den_val != 0:
            return "method_limit_direct_substitution"
    except Exception:
        pass
    return "method_limit_direct_substitution"


class LimitStepGenerator(StepGenerator):
    problem_type = "calculus_limit"

    def generate(
        self,
        expr: Any,
        symbol: Symbol | None = None,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        if not isinstance(expr, Limit):
            return [
                SolutionStep(
                    order=1,
                    description_km="គណនាលីមីត៖",
                    description_en="Evaluate the limit:",
                    expression=str(expr),
                    title_km="គណនាលីមីត",
                    title_en="Evaluate Limit",
                    rationale_km="កន្សោមមិនមែនជាទម្រង់លីមីតស្តង់ដារ។",
                    rationale_en="Expression is not in standard limit format.",
                )
            ]

        f = expr.args[0]
        var = expr.args[1] if len(expr.args) > 1 else (symbol or Symbol("x"))
        pt = expr.args[2] if len(expr.args) > 2 else S.Zero

        pt_str = _format_pt_str(pt)

        if f.has(sympy.log):
            return self._generate_logarithm_limit_steps(
                f=f,
                var=var,
                pt=pt,
                pt_str=pt_str,
                expr=expr,
                expected_rhs=expected_rhs,
            )

        # Step 1: Original Limit
        orig_latex = f"\\lim_{{{var} \\to {pt_str}}} \\left({_to_latex(f)}\\right)"
        steps.append(
            SolutionStep(
                order=order,
                description_km="កំណត់កន្សោមលីមីតដើម៖",
                description_en="Given limit expression:",
                expression=orig_latex,
                title_km="កំណត់កន្សោមលីមីតដើម",
                title_en="Identify Limit Expression",
                rationale_km=f"កត់សម្គាល់អនុគមន៍ f({var}) = {_to_latex(f)} និងចំណុចខិតជិត {var} \\to {pt_str}។",
                rationale_en=f"Identify the function f({var}) = {_to_latex(f)} and the approach point {var} -> {pt_str}.",
            )
        )
        order += 1

        # Direct substitution check
        num, den = f.as_numer_denom()

        is_indeterminate_0_0 = False
        is_indeterminate_oo_oo = False
        is_zero_denominator = False
        direct_eval_success = False
        direct_val = None
        num_val = None
        den_val = None

        if pt not in (oo, -oo):
            try:
                num_val = num.subs(var, pt)
                den_val = den.subs(var, pt)
                if num_val == 0 and den_val == 0:
                    is_indeterminate_0_0 = True
                elif den_val != 0:
                    direct_val = simplify_real_roots(num_val / den_val)
                    direct_eval_success = True
                else:
                    is_zero_denominator = True
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
                    title_km="កំណត់រាងមិនកំណត់ [0/0]",
                    title_en="Identify Indeterminate Form [0/0]",
                    rationale_km=f"ការជំនួសផ្ទាល់នាំឱ្យបានភាគយក និងភាគបែងស្មើសូន្យ ដូច្នេះត្រូវលុបរាងមិនកំណត់ [0/0]។",
                    rationale_en="Direct substitution yields 0/0, requiring algebraic transformation to cancel the zero factor.",
                    rule_formula=r"\left[\frac{0}{0}\right]",
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
                    title_km="កំណត់រាងមិនកំណត់ [∞/∞]",
                    title_en="Identify Indeterminate Form [∞/∞]",
                    rationale_km="ភាគយកនិងភាគបែងខិតជិតអនន្តដំណាលគ្នា ត្រូវទាញកត្តាដឺក្រេខ្ពស់បំផុតចេញក្រៅ។",
                    rationale_en="Numerator and denominator approach infinity, requiring highest-degree term factoring.",
                    rule_formula=r"\left[\frac{\infty}{\infty}\right]",
                )
            )
            order += 1
        elif direct_eval_success and direct_val is not None:
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ជំនួសតម្លៃ ${var} = {pt_str}$ ដោយផ្ទាល់ (អនុគមន៍ជាប់ត្រង់ ${var} = {pt_str}$)៖",
                    description_en=f"Direct substitution of ${var} = {pt_str}$ (function is continuous at ${var} = {pt_str}$):",
                    expression=f"f({pt_str}) = {latex(direct_val)}",
                    title_km="ជំនួសតម្លៃផ្ទាល់ (អនុគមន៍ជាប់)",
                    title_en="Direct Substitution (Continuous Function)",
                    rationale_km=f"អនុគមន៍កំណត់ និងជាប់ត្រង់ {var} = {pt_str} ដូច្នេះតម្លៃលីមីតស្មើនឹងតម្លៃអនុគមន៍ f({pt_str})។",
                    rationale_en=f"The function is defined and continuous at {var} = {pt_str}, so the limit equals f({pt_str}).",
                    rule_formula=r"\lim_{x \to c} f(x) = f(c)",
                )
            )
            order += 1
        elif is_zero_denominator:
            num_val_str = latex(num_val)
            if hasattr(num_val, "free_symbols") and num_val.free_symbols:
                rationale_km = (
                    f"ជំនួសតម្លៃ ${var} = {pt_str}$ នាំឱ្យភាគបែងស្មើសូន្យ ខណៈភាគយកស្មើ ${num_val_str}$។ "
                    f"ប្រសិនបើ ${num_val_str} = 0$ នោះលីមីតមានរាងមិនកំណត់ [0/0]។ ចំពោះ ${num_val_str} \\neq 0$ លីមីតខិតជិតអនន្ត។"
                )
                rationale_en = (
                    f"Direct substitution of ${var} = {pt_str}$ gives zero in denominator while numerator is ${num_val_str}$. "
                    f"If ${num_val_str} = 0$, this yields indeterminate form [0/0]. If ${num_val_str} \\neq 0$, the limit is infinite."
                )
            else:
                rationale_km = f"ជំនួសតម្លៃ ${var} = {pt_str}$ នាំឱ្យភាគបែងស្មើសូន្យ ខណៈភាគយកស្មើ ${num_val_str} \\neq 0$ (ទម្រង់ $\\frac{{k}}{{0}}$) នាំឱ្យលីមីតខិតជិតអនន្ត។"
                rationale_en = f"Direct substitution yields non-zero numerator ${num_val_str}$ over zero denominator (form $\\frac{{k}}{{0}}$), approaching infinity."

            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ជំនួសតម្លៃ ${var} = {pt_str}$ ដោយផ្ទាល់ នាំឱ្យភាគបែងស្មើសូន្យ ($den = 0$)៖",
                    description_en=f"Direct substitution of ${var} = {pt_str}$ results in zero denominator ($den = 0$):",
                    expression=f"\\frac{{{latex(num)}}}{{{latex(den)}}} \\xrightarrow{{{var} \\to {pt_str}}} \\frac{{{num_val_str}}}{{0}}",
                    title_km="ពិនិត្យការជំនួសផ្ទាល់ (ភាគបែងស្មើសូន្យ)",
                    title_en="Direct Substitution (Zero Denominator)",
                    rationale_km=rationale_km,
                    rationale_en=rationale_en,
                    rule_formula=r"\frac{k}{0} \to \infty",
                )
            )
            order += 1

        # Step 3: Transformation / Factoring / Identity
        reduced_expr = None
        if is_indeterminate_0_0:
            has_radical = any(
                isinstance(p, sympy.Pow) and p.exp.is_Rational and p.exp.q != 1
                for p in f.atoms(sympy.Pow)
            )
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
                            title_km="បំប្លែងតាមរូបមន្តត្រីកោណមាត្រ",
                            title_en="Apply Trigonometric Identities",
                            rationale_km="ប្រើរូបមន្តត្រីកោណមាត្រដើម្បីសម្រួលកន្សោម និងលុបរាងមិនកំណត់។",
                            rationale_en="Use trigonometric identities to simplify expression and eliminate indeterminate form.",
                        )
                    )
                    order += 1
            elif has_radical:
                # Radical conjugate method
                canceled_f = factor(f)
                if canceled_f != f:
                    reduced_expr = canceled_f
                steps.append(
                    SolutionStep(
                        order=order,
                        description_km=f"គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ រួចសម្រួលកត្តាសូន្យ $({var} - {pt_str})$៖",
                        description_en=f"Multiply numerator and denominator by conjugate, then cancel common factor $({var} - {pt_str})$:",
                        expression=f"{latex(f)} = {latex(reduced_expr or f)} \\quad (\\text{{ចំពោះ }} {var} \\neq {pt_str})",
                        title_km="គុណកន្សោមឆ្លាស់នៃរ៉ាឌីកាល់",
                        title_en="Multiply by Radical Conjugate",
                        rationale_km="ប្រើរូបមន្តកន្សោមឆ្លាស់ (√A - B)(√A + B) = A - B² ដើម្បីបំបាត់រ៉ាឌីកាល់ និងសម្រួលកត្តាសូន្យ។",
                        rationale_en="Use radical conjugate identity (√A - B)(√A + B) = A - B² to eliminate roots and cancel zero factor.",
                        rule_formula=r"(\sqrt{A} - B)(\sqrt{A} + B) = A - B^2",
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
                            title_km="ដាក់ជាផលគុណកត្តា និងសម្រួលកត្តាសូន្យ",
                            title_en="Factor and Cancel Common Zero Factor",
                            rationale_km=f"បំបែកពហុធាភាគយក និងភាគបែង ដើម្បីសម្រួលកត្តាសូន្យ ({var} - {pt_str}) ដែលនាំឱ្យមានរាង 0/0។",
                            rationale_en=f"Factor numerator and denominator polynomials to cancel vanishing factor ({var} - {pt_str}).",
                            rule_formula=r"\frac{(x - c)P(x)}{(x - c)Q(x)} = \frac{P(x)}{Q(x)}",
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
                            title_km="ដាក់ភាគយកនិងភាគបែងជាផលគុណកត្តា",
                            title_en="Factor Numerator & Denominator",
                            rationale_km="បំបែកពហុធាដើម្បីស្រង់កត្តារួមចេញ។",
                            rationale_en="Factor polynomials to extract common terms.",
                        )
                    )
                    order += 1

        # Step 4: Final Limit Value
        try:
            final_val = simplify_real_roots(expr.doit())
            if final_val.has(sympy.I) or "depends on" in str(final_val):
                raise ValueError("complex limit")
        except Exception:
            from app.solvers.algebra.sequence_solver import evaluate_sequence_limit
            final_val = evaluate_sequence_limit(f, var)
            if final_val is None:
                final_val = oo

        eval_expr_latex = latex(reduced_expr) if reduced_expr is not None else latex(f)

        steps.append(
            SolutionStep(
                order=order,
                description_km=f"គណនាតម្លៃលីមីតចុងក្រោយនៅពេល ${var} \\to {pt_str}$៖",
                description_en=f"Evaluate the final limit as ${var} \\to {pt_str}$:",
                expression=f"\\lim_{{{var} \\to {pt_str}}} \\left({eval_expr_latex}\\right) = {latex(final_val)}",
                title_km="គណនាតម្លៃលីមីតចុងក្រោយ",
                title_en="Compute Final Limit Value",
                rationale_km="ជំនួសតម្លៃខិតជិតចូលក្នុងកន្សោមសម្រួលរួច ដើម្បីទទួលបានតម្លៃលីមីតពិតប្រាកដ។",
                rationale_en="Substitute approach value into simplified continuous expression to evaluate exact limit value.",
            )
        )
        order += 1

        # Step 5: Verification (if expected RHS is provided, e.g. lim_{x->2} \sqrt{x} = \sqrt{2})
        if expected_rhs is not None:
            expected_rhs = simplify_real_roots(expected_rhs)
            is_match = (final_val == expected_rhs) or bool(sympy.simplify(final_val - expected_rhs) == 0)
            status_km = "ពិត" if is_match else "មិនពិត"
            status_en = "True / Verified" if is_match else "False / Not Equal"
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ផ្ទៀងផ្ទាត់សមភាព៖ តម្លៃលីមីតគណនាបាន = ${latex(final_val)}$ ស្មើនឹងអង្គខាងស្តាំ = ${latex(expected_rhs)}$ ({status_km})៖",
                    description_en=f"Verification: Computed limit = ${latex(final_val)}$ matches RHS = ${latex(expected_rhs)}$ ({status_en}):",
                    expression=f"{latex(final_val)} = {latex(expected_rhs)} \\quad \\left(\\text{{{status_km} / {status_en}}}\\right)",
                    title_km="ផ្ទៀងផ្ទាត់សមភាពនៃលីមីត",
                    title_en="Verify Limit Equality",
                    rationale_km="ប្រៀបធៀបតម្លៃលីមីតដែលបានគណនា ជាមួយនឹងអង្គខាងស្តាំនៃសមភាពដើម ដើម្បីផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវ។",
                    rationale_en="Compare calculated limit value against the right-hand side of original equality to verify correctness.",
                    is_verification=True,
                )
            )

        return steps

    def _generate_logarithm_limit_steps(
        self,
        f: Any,
        var: Symbol,
        pt: Any,
        pt_str: str,
        expr: Limit,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        final_val = simplify_real_roots(expr.doit())

        # Determine approach notation
        approach_sym = rf"{var} \to {pt_str}"
        if pt == 0:
            approach_sym = rf"{var} \to 0^+"
        elif pt == oo:
            approach_sym = rf"{var} \to +\infty"

        # Step 1: Identify original limit
        orig_latex = rf"\lim_{{{approach_sym}}} \left({_to_latex(f)}\right)"
        steps.append(
            SolutionStep(
                order=1,
                description_km="កំណត់កន្សោមលីមីតដើមនៃអនុគមន៍លោការីតនេពែ៖",
                description_en="Given natural logarithmic limit expression:",
                expression=orig_latex,
                title_km="កំណត់កន្សោមលីមីតដើម",
                title_en="Identify Limit Expression",
                rationale_km=f"កត់សម្គាល់អនុគមន៍ f({var}) = {_to_latex(f)} និងចំណុចខិតជិត ${approach_sym}$ (ដែនកំណត់នៃ $\\ln {var}$ គឺ ${var} > 0$)។",
                rationale_en=f"Identify the function f({var}) = {_to_latex(f)} and approach ${approach_sym}$ (domain of $\\ln {var}$ is ${var} > 0$).",
            )
        )

        num, den = f.as_numer_denom()

        # Step 2 & 3
        if pt == 0:
            steps.append(
                SolutionStep(
                    order=2,
                    description_km=f"នៅពេល ${approach_sym}$ យើងមាន ${var} \\to 0$ និង $\\ln {var} \\to -\\infty$ នាំឱ្យមានរាងមិនកំណត់ $[0 \\times (-\\infty)]$៖",
                    description_en=f"As ${approach_sym}$, ${var} \\to 0$ and $\\ln {var} \\to -\\infty$, yielding indeterminate form $[0 \\times (-\\infty)]:$",
                    expression=r"0 \times (-\infty) \quad \text{(រាងមិនកំណត់)}",
                    title_km="កំណត់រាងមិនកំណត់ [0 × (-∞)]",
                    title_en="Identify Indeterminate Form [0 × (-∞)]",
                    rationale_km="ការជំនួសផ្ទាល់នាំឱ្យបានរាងមិនកំណត់ [0 × (-∞)] ដូច្នេះត្រូវអនុវត្តរូបមន្តលីមីតគ្រឹះនៃអនុគមន៍លោការីតនេពែ។",
                    rationale_en="Direct substitution yields [0 × (-∞)], requiring fundamental logarithmic limit theorem.",
                    rule_formula=r"\left[0 \times (-\infty)\right]",
                )
            )
            steps.append(
                SolutionStep(
                    order=3,
                    description_km=f"អនុវត្តរូបមន្តលីមីតគ្រឹះ $\\lim_{{{var} \\to 0^+}} {var}^n \\ln {var} = 0$ (ចំពោះ $n > 0$)៖",
                    description_en=f"Apply fundamental logarithmic limit $\\lim_{{{var} \\to 0^+}} {var}^n \\ln {var} = 0$ (for $n > 0$):",
                    expression=rf"\lim_{{{approach_sym}}} \left({_to_latex(f)}\right) = {_to_latex(final_val)}",
                    title_km="អនុវត្តរូបមន្តលីមីតគ្រឹះលោការីតត្រង់ 0⁺",
                    title_en="Apply Fundamental Logarithmic Limit at 0⁺",
                    rationale_km=f"ផ្អែកតាមទ្រឹស្តីបទលីមីតគ្រឹះនៃអនុគមន៍លោការីតនេពែត្រង់ $0^+$ គេបាន $\\lim_{{{var} \\to 0^+}} {var}^n \\ln {var} = 0$។",
                    rationale_en="By fundamental logarithmic limit theorem at 0+, the limit evaluates to 0.",
                    rule_formula=rf"\lim_{{{var} \\to 0^+}} {var}^n \\ln {var} = 0 \quad (n > 0)",
                )
            )
        else:
            # pt at infinity
            steps.append(
                SolutionStep(
                    order=2,
                    description_km=f"នៅពេល ${approach_sym}$ យើងមាន $\\ln {var} \\to +\\infty$ និងភាគបែងខិតជិត $+\\infty$ នាំឱ្យមានរាងមិនកំណត់ $\\left[\\frac{{\\infty}}{{\\infty}}\\right]$៖",
                    description_en=f"As ${approach_sym}$, $\\ln {var} \\to +\\infty$ and denominator approaches $+\\infty$, yielding form $[\\infty/\\infty]$:",
                    expression=r"\frac{\infty}{\infty} \quad \text{(រាងមិនកំណត់)}",
                    title_km="កំណត់រាងមិនកំណត់ [∞/∞]",
                    title_en="Identify Indeterminate Form [∞/∞]",
                    rationale_km="ភាគយកនិងភាគបែងខិតជិតអនន្តដំណាលគ្នា ដូច្នេះត្រូវអនុវត្តរូបមន្តលីមីតគ្រឹះនៃអនុគមន៍លោការីតនេពែ។",
                    rationale_en="Numerator and denominator approach infinity, requiring fundamental logarithmic limit theorem.",
                    rule_formula=r"\left[\frac{\infty}{\infty}\right]",
                )
            )

            if isinstance(num, sympy.Add):
                split_terms = [rf"\frac{{{_to_latex(t)}}}{{{_to_latex(den)}}}" for t in num.args]
                split_str = " + ".join(split_terms)
                steps.append(
                    SolutionStep(
                        order=3,
                        description_km=f"បំបែកភាគយក និងអនុវត្តរូបមន្តលីមីតគ្រឹះ $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{var}^n}} = 0$ (ចំពោះ $n > 0$)៖",
                        description_en=f"Split numerator and apply fundamental limit $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{var}^n}} = 0$ (for $n > 0$):",
                        expression=rf"\frac{{{_to_latex(num)}}}{{{_to_latex(den)}}} = {split_str}",
                        title_km="បំបែកកន្សោម និងអនុវត្តលីមីតគ្រឹះ",
                        title_en="Split Terms and Apply Fundamental Limit",
                        rationale_km=f"ដោយសារ $\\lim_{{{var} \\to +\\infty}} \\frac{{1}}{{{_to_latex(den)}}} = 0$ និង $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{_to_latex(den)}}} = 0$ គេបានលីមីតស្មើ 0។",
                        rationale_en="Since each constituent term approaches 0 at infinity, the overall limit is 0.",
                        rule_formula=rf"\lim_{{{var} \\to +\\infty}} \frac{{\\ln {var}}}{{{var}^n}} = 0 \quad (n > 0)",
                    )
                )
            else:
                steps.append(
                    SolutionStep(
                        order=3,
                        description_km=f"អនុវត្តរូបមន្តលីមីតគ្រឹះ $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{var}^n}} = 0$ (ចំពោះ $n > 0$)៖",
                        description_en=f"Apply fundamental logarithmic limit $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{var}^n}} = 0$ (for $n > 0$):",
                        expression=rf"\lim_{{{approach_sym}}} \left({_to_latex(f)}\right) = {_to_latex(final_val)}",
                        title_km="អនុវត្តរូបមន្តលីមីតគ្រឹះលោការីតត្រង់អនន្ត",
                        title_en="Apply Fundamental Logarithmic Limit at Infinity",
                        rationale_km=f"ផ្អែកតាមទ្រឹស្តីបទលីមីតគ្រឹះនៃអនុគមន៍លោការីតនេពែត្រង់ $+\\infty$ គេបាន $\\lim_{{{var} \\to +\\infty}} \\frac{{\\ln {var}}}{{{var}^n}} = 0$។",
                        rationale_en="By fundamental logarithmic limit theorem at infinity, the limit evaluates to 0.",
                        rule_formula=rf"\lim_{{{var} \\to +\\infty}} \frac{{\\ln {var}}}{{{var}^n}} = 0 \quad (n > 0)",
                    )
                )

        # Step 4: Final Limit Value
        steps.append(
            SolutionStep(
                order=4,
                description_km=f"សន្និដ្ឋានតម្លៃលីមីតចុងក្រោយនៅពេល ${approach_sym}$៖",
                description_en=f"Conclude final limit value as ${approach_sym}$:",
                expression=rf"\lim_{{{approach_sym}}} \left({_to_latex(f)}\right) = {_to_latex(final_val)}",
                title_km="សន្និដ្ឋានតម្លៃលីមីតចុងក្រោយ",
                title_en="Conclude Final Limit Value",
                rationale_km="ទទួលបានតម្លៃលីមីតពិតប្រាកដស្របតាមកម្មវិធីសិក្សាថ្នាក់ទី១២។",
                rationale_en="Obtain exact limit value according to Grade 12 curriculum.",
            )
        )

        # Step 5: Verification (if expected RHS is provided)
        if expected_rhs is not None:
            expected_rhs = simplify_real_roots(expected_rhs)
            is_match = (final_val == expected_rhs) or bool(sympy.simplify(final_val - expected_rhs) == 0)
            status_km = "ពិត" if is_match else "មិនពិត"
            status_en = "True / Verified" if is_match else "False / Not Equal"
            steps.append(
                SolutionStep(
                    order=5,
                    description_km=f"ផ្ទៀងផ្ទាត់សមភាព៖ តម្លៃលីមីតគណនាបាន = ${_to_latex(final_val)}$ ស្មើនឹងអង្គខាងស្តាំ = ${_to_latex(expected_rhs)}$ ({status_km})៖",
                    description_en=f"Verification: Computed limit = ${_to_latex(final_val)}$ matches RHS = ${_to_latex(expected_rhs)}$ ({status_en}):",
                    expression=rf"{_to_latex(final_val)} = {_to_latex(expected_rhs)} \quad \left(\text{{{status_km} / {status_en}}}\right)",
                    title_km="ផ្ទៀងផ្ទាត់សមភាពនៃលីមីត",
                    title_en="Verify Limit Equality",
                    rationale_km="ប្រៀបធៀបតម្លៃលីមីតដែលបានគណនា ជាមួយនឹងអង្គខាងស្តាំនៃសមភាពដើម ដើម្បីផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវ។",
                    rationale_en="Compare calculated limit value against the right-hand side of original equality to verify correctness.",
                    is_verification=True,
                )
            )

        return steps
