"""
Calculus Differential Equation Solver (Grade 12 BacII Mathematics).

Solves:
1. Linear Homogeneous First-Order ODEs: y' + ay = 0 -> y = A * e^{-ax} (A in R)
2. Cauchy Initial Value Problems: y' + ay = 0, y(x0) = y0
3. Direct Integration ODEs: y' = f(x), g(x)y' = f(x)
4. Separable ODEs: y'/y = f(x)
5. Solution Verification: Show that y = f(x) satisfies F(x, y, y') = 0
"""

from __future__ import annotations

import re
from typing import Any

import sympy
from sympy import (
    Derivative,
    Eq,
    Function,
    Rational,
    Symbol,
    cos,
    dsolve,
    exp,
    integrate,
    latex,
    log,
    simplify,
    sin,
    sqrt,
)

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.differentials import detect_differential_method
from app.knowledge.registry import get_knowledge_registry
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


def _clean_ans_latex(expr_or_str: Any) -> str:
    """Format mathematical expression to clean LaTeX using standard BacII notation."""
    if isinstance(expr_or_str, str):
        text = expr_or_str
    else:
        try:
            text = latex(expr_or_str, ln_notation=True)
        except Exception:
            text = latex(expr_or_str)
    # Ensure ln notation
    text = re.sub(r"\\log\b", r"\\ln", text)
    # Replace SymPy C1 with standard Cambodian textbook constant A or C for first-order ODEs
    if "C_2" not in text and "C2" not in text and "C_{2}" not in text:
        text = re.sub(r"\bC_\{1\}\b|\bC1\b", "A", text)
    # Clean up fractions with 1
    text = re.sub(r"(?<![0-9a-zA-Z])1\s*\\frac", r"\\frac", text)
    return text


def _solve_form_ode(f_expr: sympy.Expr, var: Symbol = Symbol("x")) -> tuple[sympy.Expr, sympy.Expr, str]:
    """
    Find coefficients a, b in y'' + ay' + by = 0 such that f(var) is a solution.
    """
    f_prime = simplify(sympy.diff(f_expr, var))
    f_second = simplify(sympy.diff(f_expr, var, 2))
    a, b = sympy.symbols("a b")

    points = [0, 1, Rational(1, 2), 2, Rational(-1, 2), -1]
    sol = None
    for p1 in points:
        for p2 in points:
            if p1 == p2:
                continue
            try:
                eq1 = Eq(f_second.subs(var, p1) + a * f_prime.subs(var, p1) + b * f_expr.subs(var, p1), 0)
                eq2 = Eq(f_second.subs(var, p2) + a * f_prime.subs(var, p2) + b * f_expr.subs(var, p2), 0)
                res = sympy.solve((eq1, eq2), (a, b))
                if isinstance(res, dict) and a in res and b in res:
                    test_id = simplify(f_second + res[a] * f_prime + res[b] * f_expr)
                    if test_id == 0:
                        sol = res
                        break
            except Exception:
                continue
        if sol:
            break

    if not sol:
        ident = f_second + a * f_prime + b * f_expr
        res = sympy.solve(ident, (a, b))
        if isinstance(res, list) and res:
            sol = res[0] if isinstance(res[0], dict) else {a: res[0][0], b: res[0][1]}

    a_val = simplify(sol[a]) if sol and a in sol else sympy.Integer(0)
    b_val = simplify(sol[b]) if sol and b in sol else sympy.Integer(0)

    ode_str = "y''"
    if a_val != 0:
        if a_val == 1:
            ode_str += " + y'"
        elif a_val == -1:
            ode_str += " - y'"
        elif a_val > 0:
            ode_str += f" + {_clean_ans_latex(a_val)}y'"
        else:
            ode_str += f" - {_clean_ans_latex(abs(a_val))}y'"
    if b_val != 0:
        if b_val == 1:
            ode_str += " + y"
        elif b_val == -1:
            ode_str += " - y"
        elif b_val > 0:
            ode_str += f" + {_clean_ans_latex(b_val)}y"
        else:
            ode_str += f" - {_clean_ans_latex(abs(b_val))}y"
    ode_str += " = 0"
    return a_val, b_val, ode_str


class DifferentialSolver(BaseSolver):
    """
    Solves first-order differential equations and generates curriculum-aligned reasoning steps.
    """

    SUPPORTED_TYPES = {
        "calculus_differential_equation",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(
        self,
        parsed: ParsedMath | sympy.Expr | sympy.Eq,
        problem_type: str = "calculus_differential_equation",
        initial_conditions: dict[Any, Any] | None = None,
        domain: str | None = None,
        **kwargs: Any,
    ) -> SolveResult:
        """
        Solve differential equation analytically and produce pedagogical steps.
        """
        if not isinstance(parsed, ParsedMath):
            meta = dict(kwargs)
            if initial_conditions is not None:
                meta["initial_condition"] = initial_conditions
                meta["cauchy"] = initial_conditions
            if domain is not None:
                meta["domain"] = domain
            parsed = ParsedMath(
                raw_text="",
                sympy_expr=parsed,
                symbols=list(parsed.free_symbols) if hasattr(parsed, "free_symbols") else [],
                is_equation=isinstance(parsed, sympy.Eq) or hasattr(parsed, "lhs"),
                metadata=meta,
            )

        expr = parsed.sympy_expr
        metadata = getattr(parsed, "metadata", {}) or {}
        if initial_conditions is not None and "initial_condition" not in metadata:
            metadata["initial_condition"] = initial_conditions
        if domain is not None and "domain" not in metadata:
            metadata["domain"] = domain

        var = metadata.get("independent_var") or Symbol("x")
        y_sym = metadata.get("dependent_var") or Symbol("y")
        ics = metadata.get("cauchy") or metadata.get("initial_condition")
        domain = metadata.get("domain")
        is_verification = metadata.get("is_verification", False)
        vfunc = metadata.get("verification_func")

        y_fn = Function("y")(var)
        dy = Derivative(y_fn, var)

        # Detect curriculum method
        method = detect_differential_method(parsed)
        lesson_metadata = get_knowledge_registry().get_metadata(method.id)
        lesson_info = lesson_metadata.to_dict() if lesson_metadata else None

        generator = self._get_step_generator("calculus_differential_equation")

        # --- Handle Case 5: Solution Verification ---
        if is_verification and vfunc is not None:
            try:
                d2y = Derivative(y_fn, (var, 2))
                y_prime_val = sympy.diff(vfunc, var)
                y_second_val = sympy.diff(vfunc, var, 2)
                sub_dict = {
                    d2y: y_second_val,
                    dy: y_prime_val,
                    y_fn: vfunc,
                }
                lhs_val = simplify(expr.lhs.subs(sub_dict))
                rhs_val = simplify(expr.rhs.subs(sub_dict))
                is_valid = simplify(lhs_val - rhs_val) == 0
                ans_str = r"\text{ពិត (Verified)}" if is_valid else r"\text{មិនពិត (Not verified)}"
            except Exception as e:
                is_valid = False
                ans_str = f"Error: {e}"

            steps = []
            if generator is not None:
                try:
                    steps = generator.generate_steps(
                        equation=expr,
                        symbol=var,
                        solution=ans_str,
                        parsed=parsed,
                    )
                except Exception:
                    pass

            return SolveResult(
                answer=ans_str,
                variable=str(var),
                is_verified=is_valid,
                steps=steps,
                lesson_info=lesson_info,
                metadata={
                    "problem_type": problem_type,
                    "is_verification": True,
                    "is_valid": is_valid,
                },
            )

        # --- Handle Case 6: Form ODE from Solution ---
        is_form_ode = metadata.get("is_form_ode", False)
        d2y = Derivative(y_fn, (var, 2))
        has_derivatives = False
        if hasattr(expr, "lhs") and hasattr(expr, "rhs"):
            diff_terms = expr.lhs - expr.rhs
            if diff_terms.has(d2y) or diff_terms.has(dy):
                has_derivatives = True
        elif expr.has(dy) or expr.has(d2y):
            has_derivatives = True

        if is_form_ode or (not has_derivatives and problem_type == "calculus_differential_equation"):
            f_expr = metadata.get("function_rhs")
            if f_expr is None:
                if hasattr(expr, "rhs"):
                    f_expr = expr.rhs
                elif hasattr(expr, "lhs"):
                    f_expr = expr.lhs
                else:
                    f_expr = expr

            a_val, b_val, ode_ans_str = _solve_form_ode(f_expr, var)
            if not getattr(parsed, "metadata", None):
                parsed.metadata = {}
            parsed.metadata["a"] = a_val
            parsed.metadata["b"] = b_val
            parsed.metadata["function_rhs"] = f_expr
            parsed.metadata["is_form_ode"] = True

            steps = []
            if generator is not None:
                try:
                    steps = generator.generate_steps(
                        equation=expr,
                        symbol=var,
                        solution=ode_ans_str,
                        parsed=parsed,
                    )
                except Exception:
                    pass

            return SolveResult(
                answer=ode_ans_str,
                variable=str(var),
                is_verified=True,
                steps=steps,
                lesson_info=lesson_info,
                metadata={
                    "problem_type": problem_type,
                    "is_form_ode": True,
                    "order": 2,
                    "a": str(a_val),
                    "b": str(b_val),
                },
            )

        # --- Solve ODE ---
        ans_str = ""
        is_verified = False

        try:
            diff = expr.lhs - expr.rhs
            coeff_d2y = diff.coeff(d2y)

            # Check if second-order linear homogeneous: ay'' + by' + cy = 0
            if coeff_d2y != 0:
                coeff_dy = diff.coeff(dy)
                coeff_y = diff.coeff(y_fn)
                rem = simplify(diff - (coeff_d2y * d2y + coeff_dy * dy + coeff_y * y_fn))

                if rem == 0:
                    A = simplify(coeff_dy / coeff_d2y)
                    B = simplify(coeff_y / coeff_d2y)
                    delta = simplify(A**2 - 4 * B)

                    C1, C2 = sympy.symbols("C_1 C_2")
                    if delta > 0:
                        r1 = simplify((-A + sqrt(delta)) / 2)
                        r2 = simplify((-A - sqrt(delta)) / 2)
                        gen_expr = C1 * exp(r1 * var) + C2 * exp(r2 * var)
                        ans_str = f"y = C_1 e^{{{_clean_ans_latex(r1 * var)}}} + C_2 e^{{{_clean_ans_latex(r2 * var)}}} \\quad (C_1, C_2 \\in \\mathbb{{R}})"
                    elif delta == 0:
                        r0 = simplify(-A / 2)
                        gen_expr = (C1 * var + C2) * exp(r0 * var)
                        ans_str = f"y = (C_1 {var} + C_2) e^{{{_clean_ans_latex(r0 * var)}}} \\quad (C_1, C_2 \\in \\mathbb{{R}})"
                    else:
                        alpha = simplify(-A / 2)
                        beta = simplify(sqrt(-delta) / 2)
                        gen_expr = exp(alpha * var) * (C1 * cos(beta * var) + C2 * sin(beta * var))
                        ans_str = f"y = e^{{{_clean_ans_latex(alpha * var)}}} (C_1 \\cos({_clean_ans_latex(beta * var)}) + C_2 \\sin({_clean_ans_latex(beta * var)})) \\quad (C_1, C_2 \\in \\mathbb{{R}})"

                    # If Cauchy initial conditions are given
                    if ics:
                        c_dict = None
                        if isinstance(ics, (list, tuple)) and len(ics) == 2 and isinstance(ics[0], (list, tuple)):
                            (x0, y0), (x1, yp0) = ics
                            eq1 = Eq(gen_expr.subs(var, x0), y0)
                            yp_expr = sympy.diff(gen_expr, var)
                            eq2 = Eq(yp_expr.subs(var, x1), yp0)
                            c_dict = sympy.solve((eq1, eq2), (C1, C2))
                        elif isinstance(ics, (list, tuple)) and len(ics) == 2 and not isinstance(ics[0], (list, tuple)):
                            x0, y0 = ics
                            pass

                        if c_dict and isinstance(c_dict, dict) and C1 in c_dict and C2 in c_dict:
                            part_expr = gen_expr.subs(c_dict).expand()
                            ans_str = f"y = {_clean_ans_latex(part_expr)}"

                    is_verified = True

            # Check if linear homogeneous: y' + ay = 0
            elif diff.coeff(dy) != 0 and (diff.coeff(dy) * dy + diff.coeff(y_fn) * y_fn - diff) == 0:
                coeff_dy = diff.coeff(dy)
                coeff_y = diff.coeff(y_fn)
                # Linear homogeneous: y' + ay = 0 => a = coeff_y / coeff_dy
                a_val = simplify(coeff_y / coeff_dy)
                neg_a = simplify(-a_val)

                if ics:
                    x0_val, y0_val = ics
                    # A * e^{-a * x0} = y0 => A = y0 / e^{-a * x0}
                    exp_at_x0 = simplify(exp(neg_a * x0_val))
                    a_const = simplify(y0_val / exp_at_x0)
                    part_sol = simplify(a_const * exp(neg_a * var))
                    ans_str = f"y = {_clean_ans_latex(part_sol)}"
                else:
                    neg_a_str = _clean_ans_latex(neg_a)
                    if neg_a == 1:
                        pwr = f"{var}"
                    elif neg_a == -1:
                        pwr = f"-{var}"
                    elif ("+" in neg_a_str or "-" in neg_a_str[1:]):
                        pwr = f"({neg_a_str}){var}"
                    else:
                        pwr = f"{neg_a_str} {var}".strip()
                    ans_str = f"y = A \\cdot e^{{{pwr}}} \\quad (A \\in \\mathbb{{R}})"

                is_verified = True

            elif expr.lhs == dy / y_fn:
                # Separable: y'/y = f(x)
                f_x = expr.rhs
                f_int = integrate(f_x, var)
                if ics:
                    x0_val, y0_val = ics
                    val_x0 = simplify(f_int.subs(var, x0_val))
                    try:
                        c_val = simplify(log(y0_val) - val_x0)
                    except Exception:
                        c_val = sympy.Integer(0)
                    part_sol = simplify(exp(f_int + c_val))
                    ans_str = f"y = {_clean_ans_latex(part_sol)}"
                else:
                    ans_str = f"y = A \\cdot e^{{{_clean_ans_latex(f_int)}}} \\quad (A \\in \\mathbb{{R}})"
                is_verified = True

            else:
                # Direct integration: dy = f(x)
                f_x = simplify(-rem / coeff_dy) if coeff_dy != 0 else expr.rhs
                raw_int = integrate(f_x, var)
                # Keep polynomial terms separate rather than combining into a single fraction
                if raw_int.is_polynomial(var):
                    antideriv = raw_int.expand()
                else:
                    antideriv = simplify(raw_int)

                if ics:
                    x0_val, y0_val = ics
                    val_x0 = simplify(antideriv.subs(var, x0_val))
                    c_val = simplify(y0_val - val_x0)
                    part_sol = antideriv + c_val
                    ans_str = f"y = {_clean_ans_latex(part_sol)}"
                else:
                    ans_str = f"y = {_clean_ans_latex(antideriv)} + C \\quad (C \\in \\mathbb{{R}})"
                is_verified = True

        except Exception:
            # Fallback to sympy dsolve
            try:
                ics_dict = {Function("y")(ics[0]): ics[1]} if ics else None
                sym_sol = dsolve(expr, y_fn, ics=ics_dict) if ics_dict else dsolve(expr, y_fn)
                ans_str = _clean_ans_latex(sym_sol)
                is_verified = True
            except Exception as exc:
                ans_str = f"Cannot solve differential equation: {exc}"
                is_verified = False

        # Generate steps
        steps = []
        if generator is not None:
            try:
                steps = generator.generate_steps(
                    equation=expr,
                    symbol=var,
                    solution=ans_str,
                    parsed=parsed,
                )
            except Exception as e:
                steps = [
                    SolutionStep(
                        order=1,
                        description_km=f"កំហុសក្នុងការបង្កើតជំហាន៖ {str(e)}",
                        description_en=f"Step generation error: {str(e)}",
                        expression=str(expr),
                        title_km="កំហុសជំហាន",
                        title_en="Step Error",
                    )
                ]

        return SolveResult(
            answer=ans_str,
            variable=str(var),
            is_verified=is_verified,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "problem_type": problem_type,
                "independent_var": str(var),
                "has_initial_condition": bool(ics),
                "domain": domain,
            },
        )

    def solve_verification(
        self,
        function_rhs: sympy.Expr,
        differential_eq: sympy.Eq,
        var: Symbol = Symbol("x"),
    ) -> SolveResult:
        """
        Verify if y = function_rhs is a solution of differential_eq.
        """
        meta = {
            "is_verification": True,
            "verification_func": function_rhs,
            "differential_eq": differential_eq,
            "independent_var": var,
        }
        parsed = ParsedMath(
            raw_text="",
            sympy_expr=differential_eq,
            symbols=[var],
            is_equation=True,
            metadata=meta,
        )
        return self.solve(parsed, "calculus_differential_equation")

