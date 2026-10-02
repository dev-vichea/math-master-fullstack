"""
Calculus integral solver.
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Eq, Function, Integral, Symbol, latex, simplify

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.integrals import detect_integral_method
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class IntegralSolver(BaseSolver):
    """
    Solves calculus integration problems (indefinite and definite).

    Handles:
    - Pure indefinite integrals: ∫ f(x) dx -> F(x) + C
    - Equated integrals: I = ∫ f(x) dx or F(x) = ∫ f(x) dx
    - Definite integrals: ∫ₐᵇ f(x) dx -> numerical / symbolic value
    """

    SUPPORTED_TYPES = {
        "calculus_integral",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    @staticmethod
    def _extract_integral(expr: Any) -> tuple[Integral | None, Symbol, str, Any]:
        """
        Extract the Integral object, variable, target variable name, and optional expected RHS.

        Returns:
            (integral_obj, var, target_name, expected_rhs)
        """
        var = Symbol("x")
        target_name = "I"
        expected_rhs = None

        if isinstance(expr, Integral):
            integral_obj = expr
            if expr.limits:
                lim = expr.limits[0]
                if isinstance(lim, (tuple, list, sympy.Tuple)):
                    var = lim[0]
                else:
                    var = lim
            return integral_obj, var, target_name, None

        if isinstance(expr, Eq):
            lhs = expr.lhs
            rhs = expr.rhs

            if isinstance(rhs, Integral):
                integral_obj = rhs
                target_name = str(lhs)
                if rhs.limits:
                    lim = rhs.limits[0]
                    var = lim[0] if isinstance(lim, (tuple, list, sympy.Tuple)) else lim
                return integral_obj, var, target_name, None

            if isinstance(lhs, Integral):
                integral_obj = lhs
                target_name = "I"
                expected_rhs = rhs
                if lhs.limits:
                    lim = lhs.limits[0]
                    var = lim[0] if isinstance(lim, (tuple, list, sympy.Tuple)) else lim
                return integral_obj, var, target_name, expected_rhs

        return None, var, target_name, None

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        expr = parsed.sympy_expr

        integral_obj, var, target_name, expected_rhs = self._extract_integral(expr)

        if integral_obj is None:
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="កន្សោមមិនមែនជាអាំងតេក្រាលទេ",
                        description_en="Expression is not an integral",
                        expression=str(expr),
                        title_km="កន្សោមមិនមែនជាអាំងតេក្រាល",
                        title_en="Not an Integral",
                    )
                ],
            )

        # Detect whether it is definite or indefinite
        is_definite = bool(integral_obj.limits and len(integral_obj.limits[0]) == 3)

        # Evaluate integral
        try:
            if is_definite:
                ans_val = integral_obj.doit()
                ans_str = str(ans_val)
            else:
                integrand = integral_obj.args[0]
                method_id = detect_integral_method(integral_obj, var)
                if method_id == "method_integral_by_parts":
                    from app.reasoning.steps.calculus.integral import (
                        _decompose_by_parts,
                        _integrate_linear_pow,
                    )

                    u, dv = _decompose_by_parts(integrand, var)
                    if u is not None and dv is not None:
                        du = sympy.diff(u, var)
                        v = _integrate_linear_pow(dv, var)
                        v_du = sympy.simplify(v * du)
                        int_v_du = _integrate_linear_pow(v_du, var)
                        antideriv = sympy.factor(sympy.simplify(u * v - int_v_du))
                    else:
                        antideriv = sympy.integrate(integrand, var)
                else:
                    antideriv = sympy.integrate(integrand, var)

                if isinstance(antideriv, sympy.Piecewise):
                    antideriv = antideriv.args[0].expr
                ans_val = antideriv
                ans_str = f"{str(antideriv)} + C"
        except Exception as e:
            return SolveResult(
                answer=None,
                variable=str(var),
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km=f"មិនអាចគណនាអាំងតេក្រាលបាន៖ {str(e)}",
                        description_en=f"Unable to evaluate integral: {str(e)}",
                        expression=str(integral_obj),
                        title_km="កំហុសគណនាអាំងតេក្រាល",
                        title_en="Integration Error",
                    )
                ],
            )

        # Generate pedagogical steps
        generator = self._get_step_generator("calculus_integral")
        if generator is not None:
            steps = generator.generate(integral_obj, symbol=var, expected_rhs=expected_rhs)
        else:
            steps = [
                SolutionStep(
                    order=1,
                    description_km="គណនាអាំងតេក្រាល៖",
                    description_en="Evaluate the integral:",
                    expression=f"{integral_obj} = {ans_str}",
                    title_km="គណនាអាំងតេក្រាល",
                    title_en="Evaluate Integral",
                )
            ]

        # Lesson awareness from curriculum knowledge registry
        from app.knowledge.registry import get_knowledge_registry

        method_id = detect_integral_method(integral_obj, var)
        lesson_metadata = get_knowledge_registry().get_metadata(method_id)
        lesson_info = lesson_metadata.to_dict() if lesson_metadata else None

        # Verification check if expected RHS was provided
        is_verified = True
        if expected_rhs is not None:
            try:
                is_verified = (ans_val == expected_rhs) or bool(sympy.simplify(ans_val - expected_rhs) == 0)
            except Exception:
                is_verified = False

        return SolveResult(
            answer=ans_str,
            variable=str(var),
            is_verified=is_verified,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "integrand": str(integral_obj.args[0]),
                "variable": str(var),
                "is_definite": is_definite,
                "method_id": method_id,
            },
        )

    def solve_initial_value(
        self,
        integrand: Any,
        var: Symbol,
        x0: Any,
        y0: Any,
    ) -> SolveResult:
        """Solve particular antiderivative problem given initial condition F(x0) = y0."""
        from app.knowledge.registry import get_knowledge_registry
        from app.reasoning.steps.calculus.integral import IntegralStepGenerator

        antideriv = sympy.integrate(integrand, var)
        G_x0 = antideriv.subs(var, x0)
        c_val = sympy.simplify(y0 - G_x0)
        particular_F = sympy.simplify(antideriv + c_val)

        generator = IntegralStepGenerator()
        steps = generator.generate_initial_value_steps(integrand, var, x0, y0)

        meta = get_knowledge_registry().get_metadata("method_primitive_initial_value")
        lesson_info = meta.to_dict() if meta else None

        return SolveResult(
            answer=str(particular_F),
            variable=str(var),
            is_verified=True,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "integrand": str(integrand),
                "variable": str(var),
                "initial_x": str(x0),
                "initial_y": str(y0),
                "constant_c": str(c_val),
                "method_id": "method_primitive_initial_value",
            },
        )

    def solve_verification(
        self,
        F_expr: Any,
        f_expr: Any,
        var: Symbol,
    ) -> SolveResult:
        """Verify whether F(x) is an antiderivative of f(x) by showing F'(x) = f(x)."""
        from app.knowledge.registry import get_knowledge_registry
        from app.reasoning.steps.calculus.integral import IntegralStepGenerator

        F_deriv = sympy.diff(F_expr, var)
        is_verified = bool(sympy.simplify(F_deriv - f_expr) == 0)

        generator = IntegralStepGenerator()
        steps = generator.generate_verification_steps(F_expr, f_expr, var)

        meta = get_knowledge_registry().get_metadata("method_primitive_verification")
        lesson_info = meta.to_dict() if meta else None

        return SolveResult(
            answer="ពិត" if is_verified else "មិនពិត",
            variable=str(var),
            is_verified=is_verified,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "primitive_F": str(F_expr),
                "function_f": str(f_expr),
                "derivative_F_prime": str(F_deriv),
                "method_id": "method_primitive_verification",
            },
        )
