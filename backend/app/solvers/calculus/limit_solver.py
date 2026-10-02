"""
Calculus limit solver.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Limit, Symbol

from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.reasoning.steps.calculus.limit import detect_limit_method
from app.solvers.base import BaseSolver, SolveResult


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


class LimitSolver(BaseSolver):
    """
    Solves calculus limit problems.

    Handles:
    - Standard limits: lim_{x→a} f(x)
    - One-sided limits: lim_{x→a⁺} f(x), lim_{x→a⁻} f(x)
    - Limits at infinity: lim_{x→∞} f(x)
    - Limits with equations: f(x) = lim_{x→a} g(x) or lim_{x→a} g(x) = L

    Uses SymPy's limit evaluation with step-by-step explanation generation.
    """

    SUPPORTED_TYPES = {
        "calculus_limit",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Evaluate a limit and generate steps.

        Process:
        1. Extract the Limit object from the expression
        2. Evaluate using SymPy's .doit() method
        3. Generate steps using the limit step generator
        4. Return formatted result
        """
        expr = parsed.sympy_expr

        # Extract limit object, variable name, and optional expected RHS
        limit_obj, variable_name, expected_rhs = self._extract_limit(expr)

        if limit_obj is None:
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="កន្សោមមិនមែនជាលីមីតទេ",
                        description_en="Expression is not a limit",
                        expression=str(expr),
                        title_km="កន្សោមមិនមែនជាលីមីត",
                        title_en="Not a Limit Expression",
                    )
                ],
            )

        # Evaluate the limit
        try:
            ans_val = simplify_real_roots(limit_obj.doit())
            if ans_val.has(sympy.I) or "depends on" in str(ans_val):
                raise ValueError("Indeterminate complex limit")
            ans_str = str(ans_val)
        except Exception as e:
            # Fallback for sequence oscillating limits (e.g. (-1)^n, sin, cos at infinity)
            from app.solvers.algebra.sequence_solver import evaluate_sequence_limit

            var_sym = Symbol(variable_name) if variable_name else Symbol("n")
            fallback_val = evaluate_sequence_limit(limit_obj.args[0], var_sym)
            if fallback_val is not None:
                ans_val = fallback_val
                ans_str = str(ans_val)
            else:
                return SolveResult(
                    answer=None,
                    variable=variable_name,
                    is_verified=False,
                    steps=[
                        SolutionStep(
                            order=1,
                            description_km=f"មិនអាចគណនាលីមីតបាន៖ {str(e)}",
                            description_en=f"Unable to evaluate limit: {str(e)}",
                            expression=str(limit_obj),
                            title_km="កំហុសគណនាលីមីត",
                            title_en="Evaluation Error",
                        )
                    ],
                )


        # Generate steps using step generator if available
        generator = self._get_step_generator("calculus_limit")
        if generator is not None:
            var_sym = Symbol(variable_name) if variable_name else None
            steps = generator.generate(limit_obj, symbol=var_sym, expected_rhs=expected_rhs)
        else:
            # Fallback generic step
            steps = [
                SolutionStep(
                    order=1,
                    description_km="គណនាលីមីត៖",
                    description_en="Evaluate the limit:",
                    expression=f"{expr} = {ans_str}",
                    title_km="គណនាលីមីត",
                    title_en="Evaluate Limit",
                )
            ]

        # Lesson awareness from curriculum registry
        from app.knowledge.registry import get_knowledge_registry

        method_id = detect_limit_method(limit_obj)
        lesson_metadata = get_knowledge_registry().get_metadata(method_id)
        lesson_info = lesson_metadata.to_dict() if lesson_metadata else None

        # Verification check
        is_verified = True
        if expected_rhs is not None:
            expected_rhs = simplify_real_roots(expected_rhs)
            try:
                is_verified = (ans_val == expected_rhs) or bool(sympy.simplify(ans_val - expected_rhs) == 0)
            except Exception:
                is_verified = False

        return SolveResult(
            answer=ans_str,
            variable=variable_name,
            is_verified=is_verified,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "limit_expression": str(limit_obj.args[0]) if limit_obj.args else None,
                "limit_point": str(limit_obj.args[2]) if len(limit_obj.args) > 2 else None,
                "limit_variable": variable_name,
                "method_id": method_id,
            },
        )

    def _extract_limit(self, expr: sympy.Expr) -> tuple[Limit | None, str | None, sympy.Expr | None]:
        """
        Extract the Limit object, variable name, and optional expected RHS from the expression.

        Handles:
        1. Direct Limit: lim_{x→a} f(x)
        2. Equation with Limit on RHS: y = lim_{x→a} f(x)
        3. Equation with Limit on LHS: lim_{x→a} f(x) = sqrt(2)

        Returns:
            Tuple of (Limit object, variable name string, expected_rhs expression or None)
        """
        # Case 1: Direct limit
        if isinstance(expr, Limit):
            limit_obj = expr
            variable_name = str(limit_obj.args[1]) if len(limit_obj.args) > 1 else None
            return limit_obj, variable_name, None

        # Case 2: Equation with limit
        if isinstance(expr, Eq):
            # Check if RHS is a limit
            if isinstance(expr.rhs, Limit):
                limit_obj = expr.rhs
                if isinstance(expr.lhs, Symbol):
                    variable_name = str(expr.lhs)
                    expected_rhs = None
                else:
                    variable_name = str(limit_obj.args[1]) if len(limit_obj.args) > 1 else "x"
                    expected_rhs = expr.lhs
                return limit_obj, variable_name, expected_rhs

            # Check if LHS is a limit
            if isinstance(expr.lhs, Limit):
                limit_obj = expr.lhs
                if isinstance(expr.rhs, Symbol):
                    variable_name = str(expr.rhs)
                    expected_rhs = None
                else:
                    variable_name = str(limit_obj.args[1]) if len(limit_obj.args) > 1 else "x"
                    expected_rhs = expr.rhs
                return limit_obj, variable_name, expected_rhs

        # Not a limit expression
        return None, None, None
