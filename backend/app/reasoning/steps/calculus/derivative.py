"""
Step-by-step derivation for Calculus Derivatives (e.g. y = f(x) -> y' = f'(x)).

Designed for High School Grade 12 / Cambodian BacII National Examination:
1. Identify original function and variable:
   - f(x) or y with respect to x.
2. Apply derivative operator and linearity:
   - f'(x) = [f(x)]' applying sum/difference rules.
3. Differentiate each component using specific rules:
   - Power rule: (x^n)' = n*x^(n-1)
   - Radical chain rule: (\sqrt{u})' = u' / (2\sqrt{u})
   - Quotient rule: (u/v)' = (u'v - uv') / v^2
   - Reciprocal power rule: (1/u^n)' = -n*u' / u^(n+1)
   - Exponential rule: (e^u)' = u'*e^u
4. Algebraic simplification and factoring:
   - Common denominator, expand numerator terms, extract common factors.
5. Final derivative result:
   - State conclusion f'(x) = ... or y' = ...
"""

from __future__ import annotations

import re
from typing import Any

import sympy
from sympy import Add, Derivative, Eq, Function, Mul, Pow, Symbol, exp, factor, latex, simplify

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.derivatives import detect_derivative_method
from app.reasoning.steps.base import StepGenerator


def _to_latex(expr_or_str: Any) -> str:
    """Format mathematical expression to LaTeX using standard BacII notation (ln instead of log)."""
    if isinstance(expr_or_str, str):
        text = expr_or_str
    else:
        try:
            text = latex(expr_or_str, ln_notation=True)
        except Exception:
            text = latex(expr_or_str)
    # Ensure any remaining \log notation is converted to \ln
    text = re.sub(r"\\log\b", r"\\ln", text)
    # Clean up redundant multiplication artifacts from parser
    text = re.sub(r"\b1\s*\\cdot\s*", "", text)
    text = re.sub(r"(?<![0-9a-zA-Z])1\s*\\frac", r"\\frac", text)
    text = re.sub(r"\\left\(-1\\right\)\s*(\d+)", r"-\1", text)
    text = re.sub(r"\(-1\)\s*(\d+)", r"-\1", text)
    return text


class DerivativeStepGenerator(StepGenerator):
    problem_type = "calculus_derivative"

    def _extract_function_components(
        self,
        expr: Any,
        symbol: Symbol | None = None,
    ) -> tuple[Any, Symbol, str, str]:
        """Extract func_expr, var, func_name, and deriv_name."""
        func_expr = expr
        var = symbol or Symbol("x")
        func_name = "y"
        deriv_name = "y'"

        if isinstance(expr, Derivative):
            func_expr = expr.expr
            if expr.variables:
                var = expr.variables[0]
            func_name = "y"
            deriv_name = "y'"
            return func_expr, var, func_name, deriv_name

        if isinstance(expr, Eq):
            lhs = expr.lhs
            rhs = expr.rhs
            if isinstance(lhs, Derivative):
                func_expr = lhs.expr
                if lhs.variables:
                    var = lhs.variables[0]
                return func_expr, var, "y", "y'"
            elif isinstance(lhs, Symbol):
                func_name = str(lhs)
                deriv_name = f"{func_name}'"
                func_expr = rhs
                symbols = list(rhs.free_symbols)
                if symbols and symbol is None:
                    var = symbols[0]
            elif isinstance(lhs, Function) or (
                hasattr(lhs, "func") and hasattr(lhs.func, "__name__")
            ):
                fname = getattr(lhs.func, "__name__", "f")
                args = getattr(lhs, "args", ())
                if args and isinstance(args[0], Symbol):
                    var = args[0]
                func_name = f"{fname}({var})"
                deriv_name = f"{fname}'({var})"
                func_expr = rhs
            elif isinstance(rhs, Symbol):
                func_name = str(rhs)
                deriv_name = f"{func_name}'"
                func_expr = lhs
                symbols = list(lhs.free_symbols)
                if symbols and symbol is None:
                    var = symbols[0]
            else:
                func_expr = rhs if rhs != 0 else lhs
                symbols = list(func_expr.free_symbols)
                if symbols and symbol is None:
                    var = symbols[0]
        elif hasattr(expr, "free_symbols"):
            symbols = list(expr.free_symbols)
            if symbols and symbol is None:
                var = symbols[0]

        return func_expr, var, func_name, deriv_name

    def generate(
        self,
        expr: Any,
        symbol: Symbol | None = None,
        expected_rhs: Any = None,
    ) -> list[SolutionStep]:
        func_expr, var, func_name, deriv_name = self._extract_function_components(expr, symbol)

        # Compute derivative and simplifications
        try:
            raw_diff = sympy.diff(func_expr, var)
            factored = factor(raw_diff)
            final_ans = factored if factored != raw_diff else simplify(raw_diff)
        except Exception:
            raw_diff = func_expr
            final_ans = func_expr

        method_id = detect_derivative_method(func_expr, var)

        if method_id == "method_derivative_radical_chain":
            steps = self._generate_radical_chain_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        elif method_id == "method_derivative_reciprocal_power":
            steps = self._generate_reciprocal_power_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        elif method_id in ("method_derivative_exponential", "method_derivative_exponential_rule"):
            steps = self._generate_exponential_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        elif method_id == "method_derivative_quotient_rule":
            steps = self._generate_quotient_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        elif method_id == "method_derivative_logarithm_composite":
            steps = self._generate_logarithm_composite_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        elif method_id == "method_derivative_logarithm_product":
            steps = self._generate_logarithm_product_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )
        else:
            steps = self._generate_standard_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )

        # Standardize notation across all steps (\log -> \ln for Cambodian Grade 12 BacII)
        for s in steps:
            s.expression = _to_latex(s.expression)
            s.description_km = _to_latex(s.description_km)
            s.description_en = _to_latex(s.description_en)

        return steps

    def _generate_radical_chain_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """Steps for (\\sqrt{u})' = u' / (2\\sqrt{u})."""
        steps: list[SolutionStep] = []

        # Find the radical argument u
        radicand = None
        for p in func_expr.atoms(Pow):
            if p.exp == sympy.Rational(1, 2):
                radicand = p.base
                break
        if radicand is None:
            radicand = func_expr

        u_prime = sympy.diff(radicand, var)

        # Step 1: Identify function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {latex(func_expr)}$ និងអថេរដេរីវេ ${var}$។",
                description_en=f"Given the function ${func_name} = {latex(func_expr)}$ with respect to ${var}$.",
                expression=f"{func_name} = {latex(func_expr)}",
            )
        )

        # Step 2: Apply radical rule
        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តប្រមាណវិធីដេរីវេ",
                title_en="Apply Derivative Operator",
                description_km=(
                    f"គេបាន ${deriv_name} = ({latex(func_expr)})'$ ដោយអនុវត្តវិធានដេរីវេរ៉ាឌីកាល់ "
                    f"$(\\sqrt{{u}})' = \\frac{{u'}}{{2\\sqrt{{u}}}}$ ចំពោះ $u = {latex(radicand)}$។"
                ),
                description_en=(
                    f"Taking derivative: ${deriv_name} = ({latex(func_expr)})'$ using the radical chain rule "
                    f"$(\\sqrt{{u}})' = \\frac{{u'}}{{2\\sqrt{{u}}}}$ where $u = {latex(radicand)}$."
                ),
                expression=f"{deriv_name} = \\frac{{({latex(radicand)})'}}{{2\\sqrt{{{latex(radicand)}}}}}",
            )
        )

        # Step 3: Differentiate inner expression
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃកន្សោមខាងក្នុង",
                title_en="Differentiate Inner Expression",
                description_km=f"គណនាដេរីវេនៃតួខាងក្នុង $({latex(radicand)})' = {latex(u_prime)}$។",
                description_en=f"Differentiate inner component: $({latex(radicand)})' = {latex(u_prime)}$.",
                expression=f"{deriv_name} = \\frac{{{latex(u_prime)}}}{{2\\sqrt{{{latex(radicand)}}}}}",
            )
        )

        # Step 4: Simplify
        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោមភាគយក និងភាគបែង",
                title_en="Simplify Expression",
                description_km="សម្រួលកត្តារួមរវាងភាគយក និងភាគបែង។",
                description_en="Cancel common factors in numerator and denominator.",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {latex(final_ans)}$",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        return steps

    def _generate_reciprocal_power_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """Steps for (1/u^n)' = -n*u' / u^(n+1)."""
        steps: list[SolutionStep] = []
        num, den = func_expr.as_numer_denom()

        n = 1
        u = den
        if isinstance(den, Pow) and den.exp.is_Integer:
            n = int(den.exp)
            u = den.base

        u_prime = sympy.diff(u, var)

        # Step 1: Identify function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {latex(func_expr)}$។",
                description_en=f"Given the function ${func_name} = {latex(func_expr)}$.",
                expression=f"{func_name} = {latex(func_expr)}",
            )
        )

        # Step 2: Apply reciprocal power rule
        if n > 1:
            rule_str_km = f"(\\frac{{1}}{{u^{{{n}}}}})' = -\\frac{{{n} u'}}{{u^{{{n+1}}}}}"
            rule_str_en = f"(1/u^{{{n}}})' = -{n}*u' / u^{{{n+1}}}"
            expr_step2 = f"{deriv_name} = -\\frac{{{n}({latex(u)})'}}{{({latex(u)})^{{{n+1}}}}}"
        else:
            rule_str_km = "(\\frac{1}{u})' = -\\frac{u'}{u^2}"
            rule_str_en = "(1/u)' = -u' / u^2"
            expr_step2 = f"{deriv_name} = -\\frac{{({latex(u)})'}}{{({latex(u)})^2}}"

        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តប្រមាណវិធីដេរីវេ",
                title_en="Apply Derivative Operator",
                description_km=(
                    f"គេបាន ${deriv_name} = ({latex(func_expr)})'$ ដោយអនុវត្តវិធាន ${rule_str_km}$ "
                    f"ចំពោះ $u = {latex(u)}$។"
                ),
                description_en=(
                    f"Taking derivative: ${deriv_name} = ({latex(func_expr)})'$ using reciprocal rule ${rule_str_en}$ "
                    f"where $u = {latex(u)}$."
                ),
                expression=expr_step2,
            )
        )

        # Step 3: Differentiate inner polynomial
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃពហុធាភាគបែង",
                title_en="Differentiate Denominator Polynomial",
                description_km=f"គណនា $({latex(u)})' = {latex(u_prime)}$។",
                description_en=f"Differentiate inner component: $({latex(u)})' = {latex(u_prime)}$.",
                expression=(
                    f"{deriv_name} = -\\frac{{{n}({latex(u_prime)})}}{{({latex(u)})^{{{n+1}}}}}"
                    if n > 1
                    else f"{deriv_name} = -\\frac{{{latex(u_prime)}}}{{({latex(u)})^2}}"
                ),
            )
        )

        # Step 4: Simplify
        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោមចុងក្រោយ",
                title_en="Simplify Final Expression",
                description_km="សម្រួលមេគុណ និងកន្សោមជាផលគុណកត្តា។",
                description_en="Simplify coefficients and factored form.",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {latex(final_ans)}$",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        return steps

    def _generate_exponential_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """
        Steps for exponential functions:
        - Quotient rule e.g. e^x(1 + cos(x)) / (1 - cos(x))
        - Constant denominator e.g. (e^x + e^-x) / 2
        - Product rule e.g. x*e^-x or x^2*e^x
        - Sum / difference with quotient e.g. e^x + 3 - e^x/(e^x + 3)
        """
        # 1. Pure quotient with variable denominator
        has_var_den = False
        if isinstance(func_expr, Mul):
            for arg in func_expr.args:
                if (
                    isinstance(arg, Pow)
                    and arg.exp.is_number
                    and arg.exp < 0
                    and arg.base.has(var)
                    and not isinstance(arg.base, exp)
                ):
                    has_var_den = True
                    break
        if has_var_den:
            return self._generate_quotient_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )

        # 2. Linear sum with constant denominator e.g. (e^x + e^-x)/2
        if isinstance(func_expr, Mul):
            c = 1
            rest = []
            for a in func_expr.args:
                if a.is_number:
                    c *= a
                else:
                    rest.append(a)
            if (
                c != 1
                and getattr(c, "is_rational", False)
                and getattr(1 / c, "is_integer", False)
                and int(1 / c) > 1
            ):
                k = int(1 / c)
                u_expr = Mul(*rest) if len(rest) > 1 else rest[0]
                return self._generate_const_denom_exponential_steps(
                    u_expr, k, var, func_name, deriv_name, final_ans
                )
        elif isinstance(func_expr, Add):
            coeffs = []
            num_terms = []
            for term in func_expr.args:
                c, m = term.as_coeff_Mul()
                coeffs.append(c)
                num_terms.append(m)
            if (
                coeffs
                and len(set(coeffs)) == 1
                and getattr(coeffs[0], "is_rational", False)
                and getattr(1 / coeffs[0], "is_integer", False)
                and int(1 / coeffs[0]) > 1
            ):
                k = int(1 / coeffs[0])
                u_expr = Add(*num_terms)
                return self._generate_const_denom_exponential_steps(
                    u_expr, k, var, func_name, deriv_name, final_ans
                )

        # 3. Product rule with exponential factor e.g. x*e^-x or x^2*e^x
        if isinstance(func_expr, Mul) and func_expr.has(exp):
            return self._generate_product_exponential_steps(
                func_expr, var, func_name, deriv_name, final_ans
            )

        steps: list[SolutionStep] = []

        # Step 1: Identify function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {latex(func_expr)}$។",
                description_en=f"Given the function ${func_name} = {latex(func_expr)}$.",
                expression=f"{func_name} = {latex(func_expr)}",
            )
        )

        # Step 2: Linearity & derivative operator
        # Identify terms in func_expr
        if isinstance(func_expr, Add):
            term_diffs = []
            for t in func_expr.args:
                term_diffs.append(f"({latex(t)})'")
            expanded_deriv = " + ".join(term_diffs).replace("+ -", "- ")
        else:
            expanded_deriv = f"({latex(func_expr)})'"

        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តប្រមាណវិធីដេរីវេ",
                title_en="Apply Derivative Operator",
                description_km=f"គេបាន ${deriv_name} = [{latex(func_expr)}]' = {expanded_deriv}$។",
                description_en=f"Taking derivative: ${deriv_name} = [{latex(func_expr)}]' = {expanded_deriv}$.",
                expression=f"{deriv_name} = {expanded_deriv}",
            )
        )

        # Step 3: Differentiate components using rules
        # If there is a quotient term like e^x / (e^x + 3)
        diff_intermediate = sympy.diff(func_expr, var)
        simplified_quotient = simplify(diff_intermediate)
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃតួនិមួយៗ",
                title_en="Differentiate Each Component",
                description_km=(
                    "អនុវត្តរូបមន្ត $(e^{x})' = e^{x}$ និងវិធានផលចែក "
                    "$\\left(\\frac{u}{v}\\right)' = \\frac{u'v - uv'}{v^2}$ គេបាន ៖"
                ),
                description_en=(
                    "Applying $(e^{x})' = e^{x}$ and quotient rule "
                    "$(u/v)' = (u'v - uv')/v^2$:"
                ),
                expression=f"{deriv_name} = {latex(simplified_quotient)}",
            )
        )

        # Step 4: Common denominator & factoring
        steps.append(
            SolutionStep(
                order=4,
                title_km="តម្រូវភាគបែងរួម និងដាក់ជាផលគុណកត្តា",
                title_en="Common Denominator and Factoring",
                description_km="តម្រូវភាគបែងរួម ពង្រាយភាគយក និងដាក់ជាផលគុណកត្តារួម ៖",
                description_en="Combine over common denominator, expand numerator, and factor common terms:",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {latex(final_ans)}$",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        return steps

    def _generate_product_exponential_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """
        Steps for product of polynomial/expression and exponential: (u * e^w)' = u' e^w + u (e^w)'.
        Matches Grade 12 BacII textbook pedagogy for exercises like image3.png.
        """
        steps: list[SolutionStep] = []

        # Separate exponential factor from remaining factors
        exp_factor = None
        other_factors = []
        if isinstance(func_expr, Mul):
            for arg in func_expr.args:
                if arg.has(exp) and exp_factor is None:
                    exp_factor = arg
                else:
                    other_factors.append(arg)
        else:
            exp_factor = func_expr
            other_factors = [1]

        u = Mul(*other_factors)
        v = exp_factor
        u_prime = sympy.diff(u, var)
        v_prime = sympy.diff(v, var)
        expanded_sum = u_prime * v + u * v_prime

        # Step 1: Identify function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${_to_latex(func_name)} = {_to_latex(func_expr)}$។",
                description_en=f"Given the function ${_to_latex(func_name)} = {_to_latex(func_expr)}$.",
                expression=f"{func_name} = {_to_latex(func_expr)}",
            )
        )

        # Step 2: Apply product rule
        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តវិធានផលគុណ",
                title_en="Apply Product Rule",
                description_km=(
                    f"អនុវត្តវិធានផលគុណ $(uv)' = u'v + uv'$ ចំពោះ "
                    f"$u = {_to_latex(u)}, v = {_to_latex(v)}$។"
                ),
                description_en=(
                    f"Apply product rule $(uv)' = u'v + uv'$ where "
                    f"$u = {_to_latex(u)}, v = {_to_latex(v)}$."
                ),
                expression=f"{deriv_name} = ({_to_latex(u)})'({_to_latex(v)}) + ({_to_latex(u)})({_to_latex(v)})'",
            )
        )

        # Step 3: Differentiate each factor
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃកត្តានីមួយៗ",
                title_en="Differentiate Each Factor",
                description_km=(
                    f"គណនា $u' = ({_to_latex(u)})' = {_to_latex(u_prime)}$ និង "
                    f"$v' = ({_to_latex(v)})' = {_to_latex(v_prime)}$ គេបាន ៖"
                ),
                description_en=(
                    f"Differentiate factors: $u' = ({_to_latex(u)})' = {_to_latex(u_prime)}$ and "
                    f"$v' = ({_to_latex(v)})' = {_to_latex(v_prime)}$:"
                ),
                expression=f"{deriv_name} = ({_to_latex(u_prime)})({_to_latex(v)}) + ({_to_latex(u)})({_to_latex(v_prime)}) = {_to_latex(expanded_sum)}",
            )
        )

        # Step 4: Factor common terms
        steps.append(
            SolutionStep(
                order=4,
                title_km="ដាក់ជាផលគុណកត្តា",
                title_en="Factor Common Terms",
                description_km="ទាញកត្តារួមនៃអនុគមន៍អិចស្បូណង់ស្យែល ៖",
                description_en="Factor out common exponential terms:",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {_to_latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {_to_latex(final_ans)}$",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        return steps

    def _generate_const_denom_exponential_steps(
        self,
        u_expr: Any,
        k: int,
        var: Symbol,
        func_name: str,
        deriv_name: str,
        final_ans: Any = None,
    ) -> list[SolutionStep]:
        """
        Steps for linear exponential function over a constant denominator k:
        y = (e^x + e^-x)/k -> y' = (e^x - e^-x)/k.
        """
        steps: list[SolutionStep] = []
        u_prime = sympy.diff(u_expr, var)
        orig_str = f"\\frac{{{_to_latex(u_expr)}}}{{{k}}}"
        res_str = f"\\frac{{{_to_latex(u_prime)}}}{{{k}}}"
        if final_ans is not None:
            ans_str = _to_latex(final_ans)
        else:
            ans_str = _to_latex(simplify(u_prime / k))

        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {orig_str}$។",
                description_en=f"Given the function ${func_name} = {orig_str}$.",
                expression=f"{func_name} = {orig_str}",
            )
        )

        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តប្រមាណវិធីដេរីវេ",
                title_en="Apply Derivative Operator",
                description_km=(
                    f"អនុវត្តវិធានដេរីវេមេគុណថេរ $\\left(\\frac{{u}}{{k}}\\right)' = \\frac{{u'}}{{k}}$ "
                    f"គេបាន ${deriv_name} = \\frac{{({_to_latex(u_expr)})'}}{{{k}}}$។"
                ),
                description_en=(
                    f"Taking derivative: ${deriv_name} = \\frac{{({_to_latex(u_expr)})'}}{{{k}}}$."
                ),
                expression=f"{deriv_name} = \\frac{{({_to_latex(u_expr)})'}}{{{k}}}",
            )
        )

        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃភាគយក",
                title_en="Differentiate Numerator",
                description_km=f"គណនាដេរីវេនៃភាគយក $({_to_latex(u_expr)})' = {_to_latex(u_prime)}$ គេបាន ៖",
                description_en=f"Differentiate numerator: $({_to_latex(u_expr)})' = {_to_latex(u_prime)}$:",
                expression=f"{deriv_name} = {res_str}",
            )
        )

        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោម",
                title_en="Simplify Expression",
                description_km=f"សម្រួលកន្សោមដេរីវេចុងក្រោយ គេបាន ${deriv_name} = {ans_str}$។",
                description_en=f"Simplify resulting derivative expression: ${deriv_name} = {ans_str}$.",
                expression=f"{deriv_name} = {ans_str}",
            )
        )

        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {ans_str}$",
                description_en=f"Therefore, ${deriv_name} = {ans_str}$",
                expression=f"{deriv_name} = {ans_str}",
            )
        )

        return steps

    def _generate_quotient_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """Steps for general quotient rule (u/v)' = (u'v - uv') / v^2."""
        steps: list[SolutionStep] = []
        u, v = func_expr.as_numer_denom()
        u_prime = sympy.diff(u, var)
        v_prime = sympy.diff(v, var)

        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ផលចែក ${func_name} = {latex(func_expr)}$។",
                description_en=f"Given rational function ${func_name} = {latex(func_expr)}$.",
                expression=f"{func_name} = {latex(func_expr)}",
            )
        )

        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តវិធានផលចែក",
                title_en="Apply Quotient Rule",
                description_km=(
                    f"អនុវត្តវិធានផលចែក $\\left(\\frac{{u}}{{v}}\\right)' = \\frac{{u'v - uv'}}{{v^2}}$ "
                    f"ចំពោះ $u = {latex(u)}, v = {latex(v)}$។"
                ),
                description_en=(
                    f"Applying quotient rule $(u/v)' = (u'v - uv')/v^2$ "
                    f"with $u = {latex(u)}, v = {latex(v)}$."
                ),
                expression=f"{deriv_name} = \\frac{{({latex(u)})'({latex(v)}) - ({latex(u)})({latex(v)})'}}{{({latex(v)})^2}}",
            )
        )

        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃភាគយក និងភាគបែង",
                title_en="Differentiate Numerator and Denominator",
                description_km=f"គណនា $u' = ({latex(u)})' = {latex(u_prime)}$ និង $v' = ({latex(v)})' = {latex(v_prime)}$។",
                description_en=f"Differentiate: $u' = ({latex(u)})' = {latex(u_prime)}$ and $v' = ({latex(v)})' = {latex(v_prime)}$.",
                expression=f"{deriv_name} = \\frac{{({latex(u_prime)})({latex(v)}) - ({latex(u)})({latex(v_prime)})}}{{({latex(v)})^2}}",
            )
        )

        # Step 4: Expand and simplify numerator
        num_raw = u_prime * v - u * v_prime
        num_expanded = sympy.expand(num_raw)
        if num_expanded != num_raw:
            desc_km = f"ពង្រាយតួភាគយក និងសម្រួលកន្សោម ៖ ${_to_latex(num_raw)} = {_to_latex(num_expanded)}$។"
            desc_en = f"Expand numerator terms and simplify: ${_to_latex(num_raw)} = {_to_latex(num_expanded)}$."
        else:
            desc_km = "ពង្រាយតួភាគយក និងសម្រួលកន្សោម។"
            desc_en = "Expand numerator terms and simplify."

        steps.append(
            SolutionStep(
                order=4,
                title_km="ពង្រាយ និងសម្រួលភាគយក",
                title_en="Expand and Simplify Numerator",
                description_km=desc_km,
                description_en=desc_en,
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {latex(final_ans)}$",
                expression=f"{deriv_name} = {latex(final_ans)}",
            )
        )

        return steps

    def _generate_standard_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """Steps for standard power rule and polynomial differentiation."""
        steps: list[SolutionStep] = []

        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {latex(func_expr)}$ និងអថេរដេរីវេ ${var}$។",
                description_en=f"Given the function ${func_name} = {latex(func_expr)}$ with variable ${var}$.",
                expression=f"{func_name} = {latex(func_expr)}",
            )
        )

        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តប្រមាណវិធីដេរីវេ",
                title_en="Apply Derivative Operator",
                description_km=f"គេបាន ${deriv_name} = ({latex(func_expr)})'$ ដោយអនុវត្តវិធានដេរីវេគ្រឹះ។",
                description_en=f"Taking derivative: ${deriv_name} = ({latex(func_expr)})'$ applying basic rules.",
                expression=f"{deriv_name} = ({latex(func_expr)})'",
            )
        )

        is_log = hasattr(func_expr, "has") and func_expr.has(sympy.log)
        desc_step3_km = (
            "អនុវត្តវិធានដេរីវេនៃអនុគមន៍លោការីត $(\\ln x)' = \\frac{1}{x}$ និងផលបូក ដក។"
            if is_log
            else "អនុវត្តវិធានដេរីវេស្វ័យគុណ $(x^n)' = n x^{n-1}$ និងផលបូក ដក។"
        )
        desc_step3_en = (
            "Apply logarithmic derivative rule $(\\ln x)' = 1/x$ and sum/difference rules across terms."
            if is_log
            else "Apply power rule $(x^n)' = n x^{n-1}$ and sum/difference rules across terms."
        )

        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃតួនិមួយៗ",
                title_en="Differentiate Each Term",
                description_km=desc_step3_km,
                description_en=desc_step3_en,
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោមចុងក្រោយ",
                title_en="Simplify Expression",
                description_km="សម្រួលកន្សោម និងរៀបតាមលំដាប់ចុះ។",
                description_en="Simplify expression and arrange terms in standard order.",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {_to_latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {_to_latex(final_ans)}$",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        return steps

    def _generate_logarithm_composite_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """
        Steps for composite natural logarithm: (ln u)' = u' / u.
        Matches Cambodian Grade 12 BacII Chapter 4 Lesson 2.
        """
        steps: list[SolutionStep] = []

        # Find the inner argument of log
        u = None
        if isinstance(func_expr, sympy.log):
            u = func_expr.args[0]
        else:
            for arg in func_expr.atoms(sympy.log):
                u = arg.args[0]
                break
        if u is None:
            u = func_expr

        u_prime = sympy.diff(u, var)

        # Step 1: Identify given function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {_to_latex(func_expr)}$ និងអថេរដេរីវេ ${var}$។",
                description_en=f"Given the function ${func_name} = {_to_latex(func_expr)}$ with respect to ${var}$.",
                expression=f"{func_name} = {_to_latex(func_expr)}",
            )
        )

        # Step 2: Apply chain rule for natural logarithm
        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តវិធានដេរីវេអនុគមន៍បណ្តាក់លោការីត",
                title_en="Apply Logarithmic Chain Rule",
                description_km=(
                    f"អនុវត្តរូបមន្តដេរីវេអនុគមន៍បណ្តាក់ $(\\ln u)' = \\frac{{u'}}{{u}}$ "
                    f"ចំពោះ $u = {_to_latex(u)}$។"
                ),
                description_en=(
                    f"Apply logarithmic chain rule $(\\ln u)' = \\frac{{u'}}{{u}}$ "
                    f"where $u = {_to_latex(u)}$."
                ),
                expression=f"{deriv_name} = \\frac{{({_to_latex(u)})'}}{{{_to_latex(u)}}}",
            )
        )

        # Step 3: Differentiate inner function
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃកន្សោមខាងក្នុង",
                title_en="Differentiate Inner Expression",
                description_km=f"គណនាដេរីវេនៃកន្សោមខាងក្នុង $({_to_latex(u)})' = {_to_latex(u_prime)}$ គេបាន ៖",
                description_en=f"Differentiate inner component: $({_to_latex(u)})' = {_to_latex(u_prime)}$:",
                expression=f"{deriv_name} = \\frac{{{_to_latex(u_prime)}}}{{{_to_latex(u)}}}",
            )
        )

        # Step 4: Simplify fraction
        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោម",
                title_en="Simplify Expression",
                description_km=f"សម្រួលកន្សោមប្រភាគ គេបាន ${deriv_name} = {_to_latex(final_ans)}$។",
                description_en=f"Simplify resulting expression: ${deriv_name} = {_to_latex(final_ans)}$.",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {_to_latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {_to_latex(final_ans)}$",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        return steps

    def _generate_logarithm_product_steps(
        self, func_expr: Any, var: Symbol, func_name: str, deriv_name: str, final_ans: Any
    ) -> list[SolutionStep]:
        """
        Steps for product of polynomial/radical and logarithm: (u * v)' = u' v + u v'.
        Matches Cambodian Grade 12 BacII Chapter 4 Lesson 2.
        """
        steps: list[SolutionStep] = []

        log_factor = None
        other_factors = []
        if isinstance(func_expr, sympy.Mul):
            for arg in func_expr.args:
                if arg.has(sympy.log) and log_factor is None:
                    log_factor = arg
                else:
                    other_factors.append(arg)
        else:
            log_factor = func_expr
            other_factors = [1]

        u = sympy.Mul(*other_factors) if other_factors else sympy.S.One
        v = log_factor if log_factor is not None else func_expr

        u_prime = sympy.diff(u, var)
        v_prime = sympy.diff(v, var)
        expanded_sum = u_prime * v + u * v_prime

        # Step 1: Identify function
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់អនុគមន៍ដើម",
                title_en="Identify Given Function",
                description_km=f"យើងមានអនុគមន៍ ${func_name} = {_to_latex(func_expr)}$ និងអថេរដេរីវេ ${var}$។",
                description_en=f"Given the function ${func_name} = {_to_latex(func_expr)}$ with respect to ${var}$.",
                expression=f"{func_name} = {_to_latex(func_expr)}",
            )
        )

        # Step 2: Apply product rule
        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តវិធានផលគុណ",
                title_en="Apply Product Rule",
                description_km=(
                    f"អនុវត្តវិធានផលគុណ $(uv)' = u'v + uv'$ ចំពោះ "
                    f"$u = {_to_latex(u)}, v = {_to_latex(v)}$។"
                ),
                description_en=(
                    f"Apply product rule $(uv)' = u'v + uv'$ where "
                    f"$u = {_to_latex(u)}, v = {_to_latex(v)}$."
                ),
                expression=f"{deriv_name} = ({_to_latex(u)})'({_to_latex(v)}) + ({_to_latex(u)})({_to_latex(v)})'",
            )
        )

        # Step 3: Differentiate each factor
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាដេរីវេនៃកត្តានីមួយៗ",
                title_en="Differentiate Each Factor",
                description_km=(
                    f"គណនា $u' = ({_to_latex(u)})' = {_to_latex(u_prime)}$ និង "
                    f"$v' = ({_to_latex(v)})' = {_to_latex(v_prime)}$ គេបាន ៖"
                ),
                description_en=(
                    f"Differentiate factors: $u' = ({_to_latex(u)})' = {_to_latex(u_prime)}$ and "
                    f"$v' = ({_to_latex(v)})' = {_to_latex(v_prime)}$:"
                ),
                expression=f"{deriv_name} = ({_to_latex(u_prime)})({_to_latex(v)}) + ({_to_latex(u)})({_to_latex(v_prime)}) = {_to_latex(expanded_sum)}",
            )
        )

        # Step 4: Simplify and common denominator
        steps.append(
            SolutionStep(
                order=4,
                title_km="សម្រួលកន្សោម",
                title_en="Simplify Expression",
                description_km=f"តម្រូវភាគបែងរួម និងសម្រួលកន្សោម គេបាន ${deriv_name} = {_to_latex(final_ans)}$។",
                description_en=f"Combine terms and simplify: ${deriv_name} = {_to_latex(final_ans)}$.",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        # Step 5: Final conclusion
        steps.append(
            SolutionStep(
                order=5,
                title_km="សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ",
                title_en="State Final Derivative Result",
                description_km=f"ដូចនេះ ${deriv_name} = {_to_latex(final_ans)}$",
                description_en=f"Therefore, ${deriv_name} = {_to_latex(final_ans)}$",
                expression=f"{deriv_name} = {_to_latex(final_ans)}",
            )
        )

        return steps
