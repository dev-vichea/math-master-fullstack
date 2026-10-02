"""
Step-by-step derivation for Calculus Integrals (Indefinite & Definite).

Designed for High School Grade 12 / Cambodian BacII National Examination:
1. Identify original integral expression (∫ f(x) dx or ∫ₐᵇ f(x) dx).
2. Determine integration method and formula:
   - Power rule: ∫ xⁿ dx = xⁿ⁺¹/(n+1) + C
   - Exponential: ∫ eᵃˣ⁺ᵇ dx = (1/a)eᵃˣ⁺ᵇ + C
   - Composite exponential: ∫ u'(x) eᵘ⁽ˣ⁾ dx = eᵘ⁽ˣ⁾ + C
   - Trigonometric: ∫ sin x dx = -cos x + C, ∫ cos x dx = sin x + C, etc.
   - Integration by parts (អាំងតេក្រាលដោយផ្នែក): ∫ u dv = uv - ∫ v du (LIATE rule)
   - Logarithmic / reciprocal: ∫ 1/x dx = ln|x| + C, ∫ u'/u dx = ln|u| + C
   - Definite integrals (អាំងតេក្រាលកំណត់): [F(x)]ₐᵇ = F(b) - F(a)
3. Detailed intermediate calculation steps.
4. Conclude final symbolic antiderivative with + C or numerical definite value.
"""

from __future__ import annotations

import re
from typing import Any

import sympy
from sympy import (
    Add,
    Eq,
    Integral,
    Mul,
    Pow,
    Rational,
    Symbol,
    cos,
    exp,
    latex,
    log,
    sin,
    tan,
    trigsimp,
)

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.integrals import detect_integral_method
from app.reasoning.steps.base import StepGenerator


def _to_latex(expr_or_str: Any) -> str:
    """Convert expression or string to standard Cambodian BacII LaTeX with \\ln notation."""
    if isinstance(expr_or_str, str):
        s = expr_or_str
    else:
        s = latex(expr_or_str)
    # Replace \log with \ln for natural logarithm
    s = s.replace(r"\log", r"\ln")
    s = s.replace(r"\frac{\sin{\left(x \right)}}{\cos{\left(x \right)}}", r"\tan(x)")
    s = s.replace(r"\frac{\cos{\left(x \right)}}{\sin{\left(x \right)}}", r"\cot(x)")
    return s


def _integrate_linear_pow(expr: Any, var: Symbol) -> Any:
    """Helper to integrate (ax+b)^n without expanding it into multiple terms."""
    if isinstance(expr, Pow):
        base, p = expr.args
        db = sympy.diff(base, var)
        if db.is_number and db != 0 and p != -1:
            return (base ** (p + 1)) / (db * (p + 1))
    if isinstance(expr, Mul):
        args = list(expr.args)
        pows = [a for a in args if isinstance(a, Pow) and a.has(var)]
        if len(pows) == 1:
            p_term = pows[0]
            coeff = expr / p_term
            if coeff.is_number:
                res = _integrate_linear_pow(p_term, var)
                if res is not None:
                    return coeff * res
    return sympy.integrate(expr, var)


def _decompose_by_parts(integrand: Any, var: Symbol) -> tuple[Any, Any]:
    """Decompose integrand into u and dv using the LIATE prioritization rule."""
    if isinstance(integrand, Mul):
        args = list(integrand.args)
        log_terms = [a for a in args if a.has(log)]
        exp_terms = [a for a in args if a.has(exp)]
        trig_terms = [a for a in args if any(a.has(fn) for fn in (sin, cos, tan))]
        pow_terms = [
            a
            for a in args
            if isinstance(a, Pow) and a.base.has(var) and a.base != var
        ]
        poly_terms = [
            a for a in args if a.is_polynomial(var) and a not in pow_terms
        ]

        # 1. Logarithm: u = ln(...)
        if log_terms:
            u = sympy.Mul(*log_terms)
            dv = sympy.simplify(integrand / u)
            return u, dv

        # 2. Algebraic * Exponential: u = P(x), dv = e^(ax) dx
        if poly_terms and exp_terms:
            u = sympy.Mul(*poly_terms)
            dv = sympy.simplify(integrand / u)
            return u, dv

        # 3. Algebraic * Trigonometric: u = P(x), dv = sin/cos dx
        if poly_terms and trig_terms:
            u = sympy.Mul(*poly_terms)
            dv = sympy.simplify(integrand / u)
            return u, dv

        # 4. Algebraic * Composite power: u = P(x), dv = (ax+b)^n dx
        if poly_terms and pow_terms:
            u = sympy.Mul(*poly_terms)
            dv = sympy.simplify(integrand / u)
            return u, dv

        # Fallback split
        u = args[0]
        dv = sympy.Mul(*args[1:])
        return u, dv

    return None, None


class IntegralStepGenerator(StepGenerator):
    problem_type = "calculus_integral"

    def generate(
        self,
        expr: Any,
        symbol: Symbol | None = None,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        if not isinstance(expr, Integral):
            # Check if Eq with Integral
            if isinstance(expr, Eq):
                if isinstance(expr.rhs, Integral):
                    return self.generate(expr.rhs, symbol=symbol, expected_rhs=expr.lhs)
                if isinstance(expr.lhs, Integral):
                    return self.generate(expr.lhs, symbol=symbol, expected_rhs=expr.rhs)

            return [
                SolutionStep(
                    order=1,
                    description_km="គណនាអាំងតេក្រាល៖",
                    description_en="Evaluate the integral:",
                    expression=str(expr),
                    title_km="គណនាអាំងតេក្រាល",
                    title_en="Evaluate Integral",
                )
            ]

        # Extract integrand, variable, and bounds
        integrand = expr.args[0]
        if expr.limits:
            limit_tuple = expr.limits[0]
            if isinstance(limit_tuple, (tuple, list, sympy.Tuple)) and len(limit_tuple) == 3:
                var = limit_tuple[0]
                a_bound = limit_tuple[1]
                b_bound = limit_tuple[2]
                return self._generate_definite_steps(
                    integrand=integrand,
                    var=var,
                    a_bound=a_bound,
                    b_bound=b_bound,
                    expr=expr,
                    expected_rhs=expected_rhs,
                )
            elif isinstance(limit_tuple, (tuple, list, sympy.Tuple)):
                var = limit_tuple[0]
            else:
                var = limit_tuple
        else:
            symbols = list(integrand.free_symbols) if hasattr(integrand, "free_symbols") else []
            var = symbol or (symbols[0] if symbols else Symbol("x"))

        method_id = detect_integral_method(expr, var)

        if method_id == "method_integral_by_parts":
            return self._generate_by_parts_steps(
                integrand=integrand,
                var=var,
                expr=expr,
                expected_rhs=expected_rhs,
            )
        elif method_id == "method_integral_exp_composite":
            return self._generate_exp_composite_steps(
                integrand=integrand,
                var=var,
                expr=expr,
                expected_rhs=expected_rhs,
            )
        else:
            return self._generate_standard_indefinite_steps(
                integrand=integrand,
                var=var,
                expr=expr,
                method_id=method_id,
                expected_rhs=expected_rhs,
            )

    # -------------------------------------------------------------------------
    # 1. Definite Integrals: ∫ₐᵇ f(x) dx = [F(x)]ₐᵇ = F(b) - F(a)
    # -------------------------------------------------------------------------
    def _generate_definite_steps(
        self,
        integrand: Any,
        var: Symbol,
        a_bound: Any,
        b_bound: Any,
        expr: Integral,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        antideriv = sympy.integrate(integrand, var)
        if isinstance(antideriv, sympy.Piecewise):
            antideriv = antideriv.args[0].expr
        final_val = expr.doit()

        # Step 1: Identify Definite Integral and Bounds
        orig_latex = rf"\int_{{{_to_latex(a_bound)}}}^{{{_to_latex(b_bound)}}} \left({_to_latex(integrand)}\right) \, d{var}"
        steps.append(
            SolutionStep(
                order=1,
                description_km=f"កំណត់កន្សោមអាំងតេក្រាលកំណត់ដើម និងគោលកំណត់ $[{_to_latex(a_bound)}, {_to_latex(b_bound)}]$៖",
                description_en=f"Given definite integral and bounds $[{_to_latex(a_bound)}, {_to_latex(b_bound)}]$:",
                expression=orig_latex,
                title_km="កំណត់កន្សោមអាំងតេក្រាលកំណត់ និងគោល",
                title_en="Identify Definite Integral and Bounds",
                rationale_km=f"កំណត់អនុគមន៍ f({var}) = {_to_latex(integrand)} ជាមួយគោលក្រោម a = {_to_latex(a_bound)} និងគោលលើ b = {_to_latex(b_bound)}។",
                rationale_en=f"Identify integrand f({var}) = {_to_latex(integrand)} with lower bound a = {_to_latex(a_bound)} and upper bound b = {_to_latex(b_bound)}.",
            )
        )

        # Step 2: Find Primitive F(x)
        steps.append(
            SolutionStep(
                order=2,
                description_km=f"រកព្រីមីទីវ $F({var}) = \\int f({var}) \\, d{var}$ (ដោយមិនគិតចំនួនថេរ C)៖",
                description_en=f"Find antiderivative $F({var}) = \\int f({var}) \\, d{var}$:",
                expression=rf"F({var}) = \int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)}",
                title_km="រកព្រីមីទីវនៃអនុគមន៍ក្រោមអាំងតេក្រាល",
                title_en="Find Antiderivative F(x)",
                rationale_km=f"អនុវត្តរូបមន្តអាំងតេក្រាលគ្រឹះដើម្បីទាញរកព្រីមីទីវ F({var}) = {_to_latex(antideriv)}។",
                rationale_en=f"Apply basic integration rules to obtain antiderivative F({var}) = {_to_latex(antideriv)}.",
            )
        )

        # Step 3: Fundamental Theorem Form [F(x)]_a^b
        steps.append(
            SolutionStep(
                order=3,
                description_km="អនុវត្តទ្រឹស្តីបទគ្រឹះនៃគណិតវិភាគសម្រាប់អាំងតេក្រាលកំណត់៖",
                description_en="Apply the Fundamental Theorem of Calculus:",
                expression=rf"\int_{{{_to_latex(a_bound)}}}^{{{_to_latex(b_bound)}}} \left({_to_latex(integrand)}\right) \, d{var} = \left[{_to_latex(antideriv)}\right]_{{{_to_latex(a_bound)}}}^{{{_to_latex(b_bound)}}} = F({_to_latex(b_bound)}) - F({_to_latex(a_bound)})",
                title_km="អនុវត្តទ្រឹស្តីបទគ្រឹះនៃគណិតវិភាគ",
                title_en="Apply Fundamental Theorem of Calculus",
                rationale_km="តម្លៃអាំងតេក្រាលកំណត់ ស្មើនឹងផលដកនៃតម្លៃព្រីមីទីវត្រង់គោលលើ ដកនឹងតម្លៃព្រីមីទីវត្រង់គោលក្រោម។",
                rationale_en="The definite integral equals the antiderivative evaluated at the upper bound minus the lower bound.",
                rule_formula=r"\int_a^b f(x) \, dx = \left[F(x)\right]_a^b = F(b) - F(a)",
            )
        )

        # Step 4: Substitute Bounds F(b) - F(a)
        Fb = antideriv.subs(var, b_bound)
        Fa = antideriv.subs(var, a_bound)
        steps.append(
            SolutionStep(
                order=4,
                description_km=f"ជំនួសតម្លៃគោលលើ ${var} = {_to_latex(b_bound)}$ និងគោលក្រោម ${var} = {_to_latex(a_bound)}$៖",
                description_en=f"Substitute upper bound ${var} = {_to_latex(b_bound)}$ and lower bound ${var} = {_to_latex(a_bound)}$:",
                expression=rf"F({_to_latex(b_bound)}) - F({_to_latex(a_bound)}) = \left({_to_latex(Fb)}\right) - \left({_to_latex(Fa)}\right)",
                title_km="ជំនួសតម្លៃគោលលើ និងគោលក្រោម",
                title_en="Substitute Upper and Lower Bounds",
                rationale_km=f"គណនាតម្លៃ F({_to_latex(b_bound)}) = {_to_latex(Fb)} និង F({_to_latex(a_bound)}) = {_to_latex(Fa)} រួចធ្វើផលដក។",
                rationale_en="Compute F(b) and F(a) and subtract.",
            )
        )

        # Step 5: Final Definite Value
        steps.append(
            SolutionStep(
                order=5,
                description_km="សន្និដ្ឋានតម្លៃអាំងតេក្រាលកំណត់ចុងក្រោយ៖",
                description_en="Conclude final definite integral value:",
                expression=rf"\int_{{{_to_latex(a_bound)}}}^{{{_to_latex(b_bound)}}} \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(final_val)}",
                title_km="សន្និដ្ឋានតម្លៃអាំងតេក្រាលកំណត់ចុងក្រោយ",
                title_en="Conclude Final Definite Value",
                rationale_km="ទទួលបានតម្លៃអាំងតេក្រាលកំណត់ពិតប្រាកដស្របតាមកម្មវិធីសិក្សាថ្នាក់ទី១២។",
                rationale_en="Obtain exact definite integral value.",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # 2. Integration by Parts: ∫ u dv = uv - ∫ v du
    # -------------------------------------------------------------------------
    def _generate_by_parts_steps(
        self,
        integrand: Any,
        var: Symbol,
        expr: Integral,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        antideriv = sympy.integrate(integrand, var)

        orig_latex = rf"\int \left({_to_latex(integrand)}\right) \, d{var}"
        steps.append(
            SolutionStep(
                order=1,
                description_km="កំណត់កន្សោមអាំងតេក្រាលមិនកំណត់ដើម៖",
                description_en="Given indefinite integral expression:",
                expression=orig_latex,
                title_km="កំណត់អាំងតេក្រាលដើម",
                title_en="Identify Given Integral",
                rationale_km=f"កត់សម្គាល់អនុគមន៍ក្រោមអាំងតេក្រាលជាផលគុណ ដែលត្រូវគណនាតាមវិធីអាំងតេក្រាលដោយផ្នែក។",
                rationale_en="Identify product integrand suitable for integration by parts.",
            )
        )

        u, dv = _decompose_by_parts(integrand, var)
        if u is not None and dv is not None:
            du = sympy.diff(u, var)
            v = _integrate_linear_pow(dv, var)
            v_du = sympy.simplify(v * du)
            int_v_du = _integrate_linear_pow(v_du, var)
            antideriv = sympy.simplify(u * v - int_v_du)
            if isinstance(antideriv, sympy.Piecewise):
                antideriv = antideriv.args[0].expr

            # Step 2: Choose u and dv
            steps.append(
                SolutionStep(
                    order=2,
                    description_km="ជ្រើសរើស $u$ និង $dv$ តាមវិធានអាំងតេក្រាលដោយផ្នែក (រូបមន្ត LIATE)៖",
                    description_en="Choose $u$ and $dv$ according to integration by parts (LIATE rule):",
                    expression=rf"\begin{{cases}} u = {_to_latex(u)} \implies du = {_to_latex(du)} \, d{var} \\ dv = {_to_latex(dv)} \, d{var} \implies v = {_to_latex(v)} \end{{cases}}",
                    title_km="កំណត់ u និង dv តាមវិធានដោយផ្នែក",
                    title_en="Identify u and dv Parts",
                    rationale_km="ជ្រើសរើស u តាមលំដាប់លោការីត ពិជគណិត ត្រីកោណមាត្រ អិចស្ប៉ូណង់ស្យែល (LIATE) និងទាញរក du និង v។",
                    rationale_en="Choose u following LIATE priority and compute differential du and antiderivative v.",
                    rule_formula=r"\int u \, dv = uv - \int v \, du",
                )
            )

            # Step 3: Apply uv - ∫ v du
            uv_part = sympy.simplify(u * v)
            steps.append(
                SolutionStep(
                    order=3,
                    description_km="អនុវត្តរូបមន្តអាំងតេក្រាលដោយផ្នែក $\\int u \\, dv = uv - \\int v \\, du$៖",
                    description_en="Apply integration by parts formula $\\int u \\, dv = uv - \\int v \\, du$:",
                    expression=rf"\int \left({_to_latex(integrand)}\right) \, d{var} = \left({_to_latex(u)}\right)\left({_to_latex(v)}\right) - \int \left({_to_latex(v_du)}\right) \, d{var}",
                    title_km="អនុវត្តរូបមន្តអាំងតេក្រាលដោយផ្នែក",
                    title_en="Apply Integration by Parts Formula",
                    rationale_km=f"ជំនួស u = {_to_latex(u)}, v = {_to_latex(v)} និង v\\,du = {_to_latex(v_du)}\\,d{var} ចូលក្នុងរូបមន្ត។",
                    rationale_en="Substitute parts into the integration by parts formula.",
                    rule_formula=r"\int u \, dv = uv - \int v \, du",
                )
            )

            # Step 4: Evaluate remaining integral
            steps.append(
                SolutionStep(
                    order=4,
                    description_km=f"គណនាអាំងតេក្រាលនៅសល់ $\\int \\left({_to_latex(v_du)}\\right) \\, d{var} = {_to_latex(int_v_du)}$៖",
                    description_en=f"Evaluate the remaining integral $\\int \\left({_to_latex(v_du)}\\right) \\, d{var} = {_to_latex(int_v_du)}$:",
                    expression=rf"{_to_latex(uv_part)} - \left({_to_latex(int_v_du)}\right) = {_to_latex(antideriv)}",
                    title_km="គណនាអាំងតេក្រាលបន្ទាប់បន្សំ និងសម្រួល",
                    title_en="Evaluate Remaining Integral and Simplify",
                    rationale_km="គណនាអាំងតេក្រាល ∫ v du រួចធ្វើការសម្រួលកន្សោម និងផ្តុំតួ។",
                    rationale_en="Evaluate ∫ v du and simplify remaining expression.",
                )
            )
        else:
            antideriv = sympy.integrate(integrand, var)
            if isinstance(antideriv, sympy.Piecewise):
                antideriv = antideriv.args[0].expr
            # Fallback direct
            steps.append(
                SolutionStep(
                    order=2,
                    description_km="អនុវត្តរូបមន្តអាំងតេក្រាលដោយផ្នែក៖",
                    description_en="Apply integration by parts rule:",
                    expression=rf"\int u \, dv = uv - \int v \, du",
                    title_km="អនុវត្តរូបមន្តអាំងតេក្រាលដោយផ្នែក",
                    title_en="Apply Integration by Parts",
                    rationale_km="ប្រើប្រាស់វិធានអាំងតេក្រាលដោយផ្នែកដើម្បីគណនាព្រីមីទីវ។",
                    rationale_en="Use integration by parts to evaluate antiderivative.",
                )
            )

        # Step Final: Conclude with + C
        steps.append(
            SolutionStep(
                order=len(steps) + 1,
                description_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលមិនកំណត់ចុងក្រោយ (បូកចំនួនថេរ C)៖",
                description_en="Conclude final indefinite integral with constant C:",
                expression=rf"\int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)} + C \quad (C \in \mathbb{{R}})",
                title_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលចុងក្រោយ",
                title_en="Conclude Final Antiderivative",
                rationale_km="ទទួលបានសំណុំនៃគ្រប់ព្រីមីទីវនៃអនុគមន៍ ដោយបូកចំនួនថេរ C (C ∈ ℝ)។",
                rationale_en="Obtain full family of antiderivatives with constant C.",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # 3. Composite Exponential Form: ∫ u'(x) eᵘ⁽ˣ⁾ dx = eᵘ⁽ˣ⁾ + C
    # -------------------------------------------------------------------------
    def _generate_exp_composite_steps(
        self,
        integrand: Any,
        var: Symbol,
        expr: Integral,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        antideriv = sympy.integrate(integrand, var)

        orig_latex = rf"\int \left({_to_latex(integrand)}\right) \, d{var}"
        steps.append(
            SolutionStep(
                order=1,
                description_km="កំណត់កន្សោមអាំងតេក្រាលមិនកំណត់ដើម៖",
                description_en="Given indefinite integral expression:",
                expression=orig_latex,
                title_km="កំណត់អាំងតេក្រាលដើម",
                title_en="Identify Given Integral",
                rationale_km=f"កត់សម្គាល់អនុគមន៍ក្រោមអាំងតេក្រាល f({var}) = {_to_latex(integrand)} មានទម្រង់ទាក់ទងនឹងអនុគមន៍អិចស្ប៉ូណង់ស្យែលបណ្តាក់។",
                rationale_en="Integrand involves composite exponential form.",
            )
        )

        # Identify inner u and u'
        exp_term = next((a for a in integrand.atoms(exp)), None)
        if exp_term is not None:
            inner_u = exp_term.args[0]
            deriv_u = sympy.diff(inner_u, var)
            coeff = sympy.simplify((integrand / exp_term) / deriv_u)

            steps.append(
                SolutionStep(
                    order=2,
                    description_km=f"កំណត់អនុគមន៍ខាងក្នុង $u({var}) = {_to_latex(inner_u)}$ និងដេរីវេ $u'({var}) = {_to_latex(deriv_u)}$៖",
                    description_en=f"Identify inner function $u({var}) = {_to_latex(inner_u)}$ and derivative $u'({var}) = {_to_latex(deriv_u)}$:",
                    expression=rf"u({var}) = {_to_latex(inner_u)} \implies u'({var}) = {_to_latex(deriv_u)}",
                    title_km="កំណត់អនុគមន៍ខាងក្នុង u និងដេរីវេ u'",
                    title_en="Identify Inner Function u and u'",
                    rationale_km=f"កត់សម្គាល់ដេរីវេនៃស្វ័យគុណ ({_to_latex(inner_u)})' = {_to_latex(deriv_u)} ត្រូវគ្នានឹងកត្តាខាងក្រៅ។",
                    rationale_en="Recognize inner exponent derivative matches external multiplying factor.",
                    rule_formula=r"\int u'(x) e^{u(x)} \, dx = e^{u(x)} + C",
                )
            )

            steps.append(
                SolutionStep(
                    order=3,
                    description_km="អនុវត្តរូបមន្តអាំងតេក្រាលទម្រង់ $\\int u'(x) e^{{u(x)}} \\, dx = e^{{u(x)}} + C$៖",
                    description_en="Apply composite exponential rule $\\int u'(x) e^{{u(x)}} \\, dx = e^{{u(x)}} + C$:",
                    expression=rf"\int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)} + C",
                    title_km="អនុវត្តរូបមន្តអាំងតេក្រាលទម្រង់ u' eᵘ",
                    title_en="Apply Composite Exponential Rule",
                    rationale_km="ព្រីមីទីវនៃកន្សោមទម្រង់ u' eᵘ គឺ eᵘ។",
                    rationale_en="Antiderivative of form u' eᵘ is eᵘ.",
                    rule_formula=r"\int u'(x) e^{u(x)} \, dx = e^{u(x)} + C",
                )
            )
        else:
            steps.append(
                SolutionStep(
                    order=2,
                    description_km="អនុវត្តរូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែល៖",
                    description_en="Apply exponential integration rule:",
                    expression=rf"\int e^{{ax+b}} \, dx = \frac{{1}}{{a}} e^{{ax+b}} + C",
                    title_km="អនុវត្តរូបមន្តអិចស្ប៉ូណង់ស្យែល",
                    title_en="Apply Exponential Rule",
                    rationale_km="អនុវត្តរូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែលគ្រឹះ។",
                    rationale_en="Apply basic exponential integration rule.",
                )
            )

        # Step Final: Conclude with + C
        steps.append(
            SolutionStep(
                order=len(steps) + 1,
                description_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលមិនកំណត់ចុងក្រោយ៖",
                description_en="Conclude final indefinite integral with constant C:",
                expression=rf"\int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)} + C \quad (C \in \mathbb{{R}})",
                title_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលចុងក្រោយ",
                title_en="Conclude Final Antiderivative",
                rationale_km="ទទួលបានសំណុំនៃគ្រប់ព្រីមីទីវនៃអនុគមន៍ ដោយបូកចំនួនថេរ C (C ∈ ℝ)។",
                rationale_en="Obtain full family of antiderivatives with constant C.",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # 4. Standard Indefinite Integrals: Power, Trig, Log, Rational
    # -------------------------------------------------------------------------
    def _generate_standard_indefinite_steps(
        self,
        integrand: Any,
        var: Symbol,
        expr: Integral,
        method_id: str,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        antideriv = sympy.integrate(integrand, var)

        orig_latex = rf"\int \left({_to_latex(integrand)}\right) \, d{var}"
        steps.append(
            SolutionStep(
                order=1,
                description_km="កំណត់កន្សោមអាំងតេក្រាលមិនកំណត់ដើម៖",
                description_en="Given indefinite integral expression:",
                expression=orig_latex,
                title_km="កំណត់អាំងតេក្រាលដើម",
                title_en="Identify Given Integral",
                rationale_km=f"កត់សម្គាល់អនុគមន៍ f({var}) = {_to_latex(integrand)} និងអថេរអាំងតេក្រាល d{var}។",
                rationale_en=f"Identify integrand f({var}) = {_to_latex(integrand)} with differential d{var}.",
            )
        )

        if method_id == "method_integral_trigonometric":
            rule_formula = r"\int \sin x \, dx = -\cos x + C, \quad \int \cos x \, dx = \sin x + C"
            title_km = "អនុវត្តរូបមន្តអាំងតេក្រាលត្រីកោណមាត្រ"
            desc_km = "អនុវត្តរូបមន្តអាំងតេក្រាលត្រីកោណមាត្រគ្រឹះ $\\int \\sin x \\, dx = -\\cos x + C$ និង $\\int \\cos x \\, dx = \\sin x + C$៖"
        elif method_id == "method_integral_exponential":
            rule_formula = r"\int e^{ax+b} \, dx = \frac{1}{a} e^{ax+b} + C"
            title_km = "អនុវត្តរូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែល"
            desc_km = "អនុវត្តរូបមន្តអាំងតេក្រាលអិចស្ប៉ូណង់ស្យែល $\\int e^{{ax+b}} \\, dx = \\frac{{1}}{{a}} e^{{ax+b}} + C$៖"
        elif method_id == "method_integral_logarithmic":
            rule_formula = r"\int \frac{1}{x} \, dx = \ln|x| + C, \quad \int \frac{u'}{u} \, dx = \ln|u| + C"
            title_km = "អនុវត្តរូបមន្តអាំងតេក្រាលលោការីតនេពែ"
            desc_km = "អនុវត្តរូបមន្តអាំងតេក្រាលនាំទៅរកលោការីតនេពែ $\\int \\frac{{1}}{{x}} \\, dx = \\ln|x| + C$៖"
        elif method_id == "method_integral_rational_power":
            rule_formula = r"\int \frac{1}{\sqrt{x}} \, dx = 2\sqrt{x} + C, \quad \int x^{-n} \, dx = \frac{x^{-n+1}}{-n+1} + C"
            title_km = "បំប្លែងស្វ័យគុណសនិទាន និងរ៉ាឌីកាល់"
            desc_km = "បំប្លែងរ៉ាឌីកាល់ ឬភាគបែងជាស្វ័យគុណសនិទាន រួចអនុវត្តរូបមន្តស្វ័យគុណ៖"
        else:
            rule_formula = r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C \quad (n \neq -1)"
            title_km = "អនុវត្តវិធានអាំងតេក្រាលស្វ័យគុណ"
            desc_km = "អនុវត្តរូបមន្តអាំងតេក្រាលស្វ័យគុណ $\\int x^n \\, dx = \\frac{{x^{{n+1}}}}{{n+1}} + C$៖"

        steps.append(
            SolutionStep(
                order=2,
                description_km=desc_km,
                description_en="Apply standard integration rule:",
                expression=rule_formula,
                title_km=title_km,
                title_en="Identify Integration Rule",
                rationale_km="កំណត់រូបមន្តគរុកោសល្យត្រឹមត្រូវសម្រាប់អនុគមន៍ក្រោមអាំងតេក្រាល។",
                rationale_en="Identify appropriate curriculum integration formula.",
                rule_formula=rule_formula,
            )
        )

        # Step 3: Check if simplification or expansion is pedagogical
        integrand_eval = integrand
        num, den = integrand.as_numer_denom()
        if den != 1 and den.has(var):
            canceled = sympy.cancel(integrand)
            if canceled.as_numer_denom()[1] == 1 or canceled != integrand:
                if not canceled.has(log) and not integrand.has(log):
                    integrand_eval = canceled
        elif isinstance(integrand, Pow) and integrand.exp == 2:
            if integrand.has(exp) or integrand.is_polynomial(var):
                integrand_eval = sympy.expand(integrand)

        if integrand_eval != integrand:
            steps.append(
                SolutionStep(
                    order=len(steps) + 1,
                    description_km="សម្រួល ឬពន្លាតកន្សោមក្រោមអាំងតេក្រាលជាមុន៖",
                    description_en="Simplify or expand the integrand first:",
                    expression=rf"{_to_latex(integrand)} = {_to_latex(integrand_eval)}",
                    title_km="សម្រួល ឬពន្លាតកន្សោមក្រោមអាំងតេក្រាល",
                    title_en="Simplify or Expand Integrand",
                    rationale_km="ធ្វើការសម្រួលប្រភាគ ឬពន្លាតកន្សោមស្វ័យគុណ ដើម្បីងាយស្រួលអនុវត្តរូបមន្តអាំងតេក្រាលតាមតួនិមួយៗ។",
                    rationale_en="Simplify fraction or expand power to facilitate term-by-term integration.",
                )
            )
            integrand_for_terms = integrand_eval
        else:
            integrand_for_terms = integrand

        # Step 4: Term-by-term computation
        if isinstance(integrand_for_terms, Add):
            term_integrals = []
            for t in integrand_for_terms.args:
                it = sympy.integrate(t, var)
                term_integrals.append(rf"\int \left({_to_latex(t)}\right) \, d{var} = {_to_latex(it)}")

            term_str = ", \\quad ".join(term_integrals)
            steps.append(
                SolutionStep(
                    order=len(steps) + 1,
                    description_km="គណនាអាំងតេក្រាលនៃតួនិមួយៗតាមវិធានផលបូក ដក៖",
                    description_en="Integrate term by term:",
                    expression=term_str,
                    title_km="គណនាព្រីមីទីវនៃតួនិមួយៗ",
                    title_en="Integrate Term by Term",
                    rationale_km="អាំងតេក្រាលនៃផលបូក ស្មើនឹងផលបូកនៃអាំងតេក្រាលតួនិមួយៗ។",
                    rationale_en="The integral of a sum equals the sum of integrals.",
                )
            )

        # Step Final: Antiderivative Conclusion
        steps.append(
            SolutionStep(
                order=len(steps) + 1,
                description_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលមិនកំណត់ចុងក្រោយ (បូកចំនួនថេរ C)៖",
                description_en="Conclude final indefinite integral with constant C:",
                expression=rf"\int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)} + C \quad (C \in \mathbb{{R}})",
                title_km="សន្និដ្ឋានចម្លើយអាំងតេក្រាលចុងក្រោយ",
                title_en="Conclude Final Antiderivative",
                rationale_km="ទទួលបានសំណុំនៃគ្រប់ព្រីមីទីវនៃអនុគមន៍ ដោយបូកចំនួនថេរ C (C ∈ ℝ)។",
                rationale_en="Obtain full family of antiderivatives with constant C.",
            )
        )

        return steps

    def generate_initial_value_steps(
        self,
        integrand: Any,
        var: Symbol,
        x0: Any,
        y0: Any,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        antideriv = sympy.integrate(integrand, var)
        G_x0 = antideriv.subs(var, x0)
        c_val = sympy.simplify(y0 - G_x0)
        particular_F = sympy.simplify(antideriv + c_val)

        # Step 1: Identify function and initial condition
        steps.append(
            SolutionStep(
                order=1,
                description_km=f"កំណត់អនុគមន៍ $f({var}) = {_to_latex(integrand)}$ និងលក្ខខណ្ឌដើម $F({_to_latex(x0)}) = {_to_latex(y0)}$៖",
                description_en=f"Given function $f({var}) = {_to_latex(integrand)}$ and initial condition $F({_to_latex(x0)}) = {_to_latex(y0)}$:",
                expression=rf"f({var}) = {_to_latex(integrand)}, \quad F({_to_latex(x0)}) = {_to_latex(y0)}",
                title_km="កំណត់អនុគមន៍ និងលក្ខខណ្ឌដើម",
                title_en="Identify Function and Initial Condition",
                rationale_km=f"ស្វែងរកព្រីមីទីវ F({var}) ដែលផ្ទៀងផ្ទាត់ F'({var}) = f({var}) និងឆ្លងកាត់ចំណុច ({_to_latex(x0)}, {_to_latex(y0)})។",
                rationale_en=f"Find particular primitive F({var}) satisfying initial condition at {_to_latex(x0)}.",
            )
        )

        # Step 2: General antiderivative
        steps.append(
            SolutionStep(
                order=2,
                description_km=f"រកព្រីមីទីវទូទៅ $F({var}) = \\int f({var}) \\, d{var} + c$៖",
                description_en=f"Find general antiderivative $F({var}) = \\int f({var}) \\, d{var} + c$:",
                expression=rf"F({var}) = \int \left({_to_latex(integrand)}\right) \, d{var} = {_to_latex(antideriv)} + c \quad (c \in \mathbb{{R}})",
                title_km="រកព្រីមីទីវទូទៅ",
                title_en="Find General Antiderivative",
                rationale_km=f"គណនាអាំងតេក្រាលមិនកំណត់ដើម្បីទទួលបានទម្រង់ព្រីមីទីវទូទៅដែលមានចំនួនថេរ c។",
                rationale_en="Integrate function to get general primitive with arbitrary constant c.",
            )
        )

        # Step 3: Solve for constant c
        steps.append(
            SolutionStep(
                order=3,
                description_km=f"ជំនួសលក្ខខណ្ឌដើម ${var} = {_to_latex(x0)}$ និង $F({_to_latex(x0)}) = {_to_latex(y0)}$ ដើម្បីរកចំនួនថេរ $c$៖",
                description_en=f"Substitute initial condition ${var} = {_to_latex(x0)}$ to solve for constant $c$:",
                expression=rf"F({_to_latex(x0)}) = {_to_latex(G_x0)} + c = {_to_latex(y0)} \implies c = {_to_latex(c_val)}",
                title_km="ជំនួសលក្ខខណ្ឌដើមដើម្បីរកចំនួនថេរ c",
                title_en="Solve for Constant c",
                rationale_km=f"ដោះស្រាយសមីការដើម្បីកំណត់តម្លៃពិតប្រាកដនៃចំនួនថេរ c = {_to_latex(c_val)}។",
                rationale_en=f"Solve equation to determine unique constant c = {_to_latex(c_val)}.",
            )
        )

        # Step 4: Particular antiderivative
        steps.append(
            SolutionStep(
                order=4,
                description_km="សន្និដ្ឋានព្រីមីទីវផ្ទៀងផ្ទាត់លក្ខខណ្ឌដើមចុងក្រោយ៖",
                description_en="Conclude particular antiderivative satisfying initial condition:",
                expression=rf"F({var}) = {_to_latex(particular_F)}",
                title_km="សន្និដ្ឋានព្រីមីទីវផ្ទៀងផ្ទាត់លក្ខខណ្ឌដើម",
                title_en="Conclude Particular Antiderivative",
                rationale_km="ជំនួសចំនួនថេរ c ដែលរកឃើញចូលក្នុងកន្សោមព្រីមីទីវទូទៅ។",
                rationale_en="Substitute constant c into general antiderivative.",
            )
        )

        return steps

    def generate_verification_steps(
        self,
        F_expr: Any,
        f_expr: Any,
        var: Symbol,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        F_deriv = sympy.diff(F_expr, var)
        simplified_deriv = sympy.simplify(F_deriv)
        is_equal = bool(sympy.simplify(simplified_deriv - f_expr) == 0)
        status_km = "ពិត" if is_equal else "មិនពិត"
        status_en = "Verified" if is_equal else "Not Equal"

        # Step 1: Definition
        steps.append(
            SolutionStep(
                order=1,
                description_km=f"រំលឹកនិយមន័យព្រីមីទីវ៖ $F({var})$ ជាព្រីមីទីវនៃ $f({var}) \\iff F'({var}) = f({var})$៖",
                description_en=f"Recall definition: $F({var})$ is an antiderivative of $f({var}) \\iff F'({var}) = f({var})$:",
                expression=rf"F({var}) = {_to_latex(F_expr)}, \quad f({var}) = {_to_latex(f_expr)}",
                title_km="រំលឹកនិយមន័យព្រីមីទីវ",
                title_en="Recall Definition of Primitive",
                rationale_km=f"ដើម្បីបង្ហាញថា F({var}) ជាព្រីមីទីវនៃ f({var}) យើងត្រូវគណនាដេរីវេ F'({var}) រួចប្រៀបធៀបជាមួយ f({var})។",
                rationale_en="To verify F(x) is primitive of f(x), compute derivative F'(x) and compare with f(x).",
                rule_formula=r"F'(x) = f(x)",
            )
        )

        # Step 2: Compute derivative F'(x)
        steps.append(
            SolutionStep(
                order=2,
                description_km=f"គណនាដេរីវេនៃអនុគមន៍ $F({var})$៖",
                description_en=f"Compute the derivative of $F({var})$:",
                expression=rf"F'({var}) = \left({_to_latex(F_expr)}\right)' = {_to_latex(F_deriv)}",
                title_km="គណនាដេរីវេ F'(x)",
                title_en="Compute Derivative F'(x)",
                rationale_km="អនុវត្តវិធានដេរីវេលើកន្សោម F(x)។",
                rationale_en="Apply differentiation rules to F(x).",
            )
        )

        # Step 3: Simplify derivative
        steps.append(
            SolutionStep(
                order=3,
                description_km=f"សម្រួលកន្សោមដេរីវេ $F'({var})$៖",
                description_en=f"Simplify derivative expression $F'({var})$:",
                expression=rf"F'({var}) = {_to_latex(simplified_deriv)}",
                title_km="សម្រួលកន្សោមដេរីវេ",
                title_en="Simplify Derivative",
                rationale_km="ធ្វើការសម្រួលកន្សោមដេរីវេឱ្យដល់ទម្រង់សាមញ្ញបំផុត។",
                rationale_en="Simplify the derivative expression.",
            )
        )

        # Step 4: Conclude verification
        steps.append(
            SolutionStep(
                order=4,
                description_km=f"ប្រៀបធៀប $F'({var})$ ជាមួយ $f({var})$ ({status_km})៖",
                description_en=f"Compare $F'({var})$ with $f({var})$ ({status_en}):",
                expression=rf"F'({var}) = {_to_latex(simplified_deriv)} = f({var}) \quad \left(\text{{{status_km}}}\right)",
                title_km="សន្និដ្ឋានការផ្ទៀងផ្ទាត់ព្រីមីទីវ",
                title_en="Conclude Antiderivative Verification",
                rationale_km=f"ដោយសារ F'({var}) = f({var}) ដូច្នេះ F({var}) ពិតជាព្រីមីទីវនៃ f({var})។",
                rationale_en="Since F'(x) = f(x), F(x) is verified to be a primitive of f(x).",
                is_verification=True,
            )
        )

        return steps
