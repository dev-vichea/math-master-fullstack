"""
Calculus derivative solver.
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Derivative, Eq, Function, Symbol, factor, latex, simplify

from app.api.schemas.responses import SolutionStep
from app.knowledge.lessons.derivatives import detect_derivative_method
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class DerivativeSolver(BaseSolver):
    """
    Solves calculus differentiation problems.

    Handles:
    - Explicit equations: y = f(x) -> y' = f'(x)
    - Functional equations: f(x) = ... -> f'(x) = ...
    - Direct expressions: f(x) -> f'(x)
    - Derivative notation: d/dx(f(x)) or Derivative(f(x), x)
    """

    SUPPORTED_TYPES = {
        "calculus_derivative",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    @staticmethod
    def _extract_function_and_var(
        expr: Any,
    ) -> tuple[Any, Symbol, str, str, Any]:
        """
        Extract the target expression, variable, function name, derivative symbol, and expected RHS.

        Returns:
            (func_expr, var, func_name, deriv_name, expected_rhs)
        """
        func_expr = expr
        var = Symbol("x")
        func_name = "y"
        deriv_name = "y'"
        expected_rhs = None

        if isinstance(expr, Derivative):
            func_expr = expr.expr
            if expr.variables:
                var = expr.variables[0]
            func_name = "y"
            deriv_name = "y'"
            return func_expr, var, func_name, deriv_name, None

        if isinstance(expr, Eq):
            lhs = expr.lhs
            rhs = expr.rhs

            # Case: Derivative(y, x) = rhs or y' = rhs
            if isinstance(lhs, Derivative):
                func_expr = lhs.expr
                if lhs.variables:
                    var = lhs.variables[0]
                expected_rhs = rhs
                return func_expr, var, "y", "y'", expected_rhs

            # Case: y = f(x) or f(x) = expr
            if isinstance(lhs, Symbol):
                func_name = str(lhs)
                deriv_name = f"{func_name}'"
                func_expr = rhs
                symbols = list(rhs.free_symbols)
                if symbols:
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
                if symbols:
                    var = symbols[0]
            else:
                # Fallback: differentiate the whole relation or rhs
                func_expr = rhs if rhs != 0 else lhs
                symbols = list(func_expr.free_symbols)
                if symbols:
                    var = symbols[0]

        elif hasattr(expr, "free_symbols"):
            symbols = list(expr.free_symbols)
            if symbols:
                var = symbols[0]

        return func_expr, var, func_name, deriv_name, expected_rhs

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Differentiate the expression and generate step-by-step reasoning.
        """
        expr = parsed.sympy_expr

        (
            func_expr,
            var,
            func_name,
            deriv_name,
            expected_rhs,
        ) = self._extract_function_and_var(expr)

        # Differentiate
        try:
            raw_diff = sympy.diff(func_expr, var)
            factored = factor(raw_diff)
            ans_val = factored if factored != raw_diff else simplify(raw_diff)
            ans_str = str(ans_val)
        except Exception as e:
            return SolveResult(
                answer=None,
                variable=str(var),
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km=f"មិនអាចគណនាដេរីវេបានទេ៖ {str(e)}",
                        description_en=f"Unable to differentiate expression: {str(e)}",
                        expression=str(expr),
                        title_km="កំហុសគណនាដេរីវេ",
                        title_en="Differentiation Error",
                    )
                ],
            )

        # Generate steps using step generator
        generator = self._get_step_generator("calculus_derivative")
        if generator is not None:
            steps = generator.generate(expr, symbol=var, expected_rhs=expected_rhs)
        else:
            steps = [
                SolutionStep(
                    order=1,
                    description_km=f"គណនាដេរីវេ {deriv_name} = ({latex(func_expr)})'",
                    description_en=f"Compute derivative {deriv_name} = ({latex(func_expr)})'",
                    expression=f"{deriv_name} = {latex(ans_val)}",
                    title_km="គណនាដេរីវេ",
                    title_en="Differentiate Expression",
                )
            ]

        # Pedagogical lesson metadata from curriculum knowledge base
        from app.knowledge.registry import get_knowledge_registry

        method_id = detect_derivative_method(func_expr, var)
        lesson_metadata = get_knowledge_registry().get_metadata(method_id)
        lesson_info = lesson_metadata.to_dict() if lesson_metadata else None

        # Verification check
        is_verified = True
        if expected_rhs is not None:
            try:
                is_verified = (ans_val == expected_rhs) or bool(
                    simplify(ans_val - expected_rhs) == 0
                )
            except Exception:
                is_verified = False

        return SolveResult(
            answer=ans_str,
            variable=str(var),
            steps=steps,
            is_verified=is_verified,
            lesson_info=lesson_info,
        )
