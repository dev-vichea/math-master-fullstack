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
from sympy import Derivative, Eq, Function, Symbol, dsolve, exp, integrate, latex, log, simplify

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
    # Replace SymPy C1 with standard Cambodian textbook constant A or C
    text = re.sub(r"\bC_\{1\}\b|\bC1\b", "A", text)
    # Clean up fractions with 1
    text = re.sub(r"(?<![0-9a-zA-Z])1\s*\\frac", r"\\frac", text)
    return text


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
        ics = metadata.get("initial_condition") or metadata.get("cauchy")
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
                y_prime_val = sympy.diff(vfunc, var)
                sub_dict = {dy: y_prime_val, y_fn: vfunc}
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

        # --- Solve ODE ---
        ans_str = ""
        is_verified = False

        try:
            # Check if linear homogeneous: y' + ay = 0
            diff = expr.lhs - expr.rhs
            coeff_dy = diff.coeff(dy)
            coeff_y = diff.coeff(y_fn)
            rem = simplify(diff - (coeff_dy * dy + coeff_y * y_fn))

            if coeff_dy != 0 and coeff_y != 0 and rem == 0:
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

