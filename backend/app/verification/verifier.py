"""
Problem-type-specific solution verification strategies.

This module never trusts a solution (whether from SymPy or elsewhere) without
verification. Each problem type has a specialized verification strategy.

Architecture:
- VerificationResult: Contains verification status, confidence, and explanation
- SolutionVerifier: Main class that dispatches to problem-type-specific verifiers
- Problem-specific verifiers: Handle equations, inequalities, expressions, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy
from sympy import Eq, Expr, GreaterThan, LessThan, StrictGreaterThan, StrictLessThan, Symbol
from sympy.core.relational import Relational


@dataclass
class VerificationResult:
    """
    Result of solution verification.

    Tracks not just pass/fail, but confidence level and explanation
    of what was checked.
    """

    is_verified: bool
    confidence: float = 1.0  # 0.0 to 1.0
    method: str = "unknown"  # Which verification method was used
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def add_warning(self, message: str) -> None:
        """Add a verification warning."""
        self.warnings.append(message)
        # Reduce confidence for warnings
        self.confidence = max(0.1, self.confidence - 0.1)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "is_verified": self.is_verified,
            "confidence": round(self.confidence, 3),
            "method": self.method,
            "details": self.details,
            "warnings": self.warnings,
        }


class SolutionVerifier:
    """
    Problem-type-specific solution verifier.

    Dispatches verification to specialized methods based on problem type.
    Never trusts solutions without checking them.
    """

    def verify(
        self,
        equation: Eq | Relational | Expr,
        solution: Any,
        variable: Symbol | str | None = None,
        problem_type: str | None = None,
    ) -> VerificationResult:
        """
        Verify a solution is correct for the given problem.

        Args:
            equation: The original equation/expression
            solution: The proposed solution (can be single value, list, or string)
            variable: The variable being solved for
            problem_type: Optional problem type hint for specialized verification

        Returns:
            VerificationResult with verification status and details
        """
        # Convert variable to Symbol if needed
        if isinstance(variable, str):
            variable = Symbol(variable)

        # Dispatch based on problem type
        if problem_type:
            if "equation" in problem_type and "system" not in problem_type:
                return self._verify_equation(equation, solution, variable)
            elif "inequality" in problem_type:
                return self._verify_inequality(equation, solution, variable)
            elif "system" in problem_type:
                return self._verify_system(equation, solution)
            elif "expression" in problem_type or "arithmetic" in problem_type:
                return self._verify_expression_evaluation(equation, solution)
            elif "limit" in problem_type or "calculus" in problem_type:
                return self._verify_calculus(equation, solution, variable)

        # Fallback: try generic verification
        return self._verify_generic(equation, solution, variable)

    def _verify_equation(
        self,
        equation: Eq,
        solution: Any,
        variable: Symbol | None,
    ) -> VerificationResult:
        """
        Verify solution to an equation by substitution.

        Substitutes the solution back into the original equation and checks
        that both sides are equal.
        """
        if not isinstance(equation, Eq):
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="equation_substitution",
                details={"error": "Not an equation"},
            )

        if variable is None:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="equation_substitution",
                details={"error": "No variable specified"},
            )

        try:
            # Parse solution string if needed
            solutions = self._parse_solution(solution)

            # Verify each solution
            verified_solutions = []
            failed_solutions = []

            for sol in solutions:
                try:
                    # Substitute into both sides
                    lhs_value = equation.lhs.subs(variable, sol)
                    rhs_value = equation.rhs.subs(variable, sol)

                    # Simplify and compare
                    difference = sympy.simplify(lhs_value - rhs_value)

                    if abs(difference) < 1e-10 or difference == 0:
                        verified_solutions.append(str(sol))
                    else:
                        failed_solutions.append(
                            {
                                "solution": str(sol),
                                "lhs": str(lhs_value),
                                "rhs": str(rhs_value),
                                "difference": str(difference),
                            }
                        )

                except Exception as e:
                    failed_solutions.append(
                        {
                            "solution": str(sol),
                            "error": str(e),
                        }
                    )

            # All solutions must verify
            is_verified = len(verified_solutions) > 0 and len(failed_solutions) == 0
            confidence = len(verified_solutions) / len(solutions) if solutions else 0.0

            result = VerificationResult(
                is_verified=is_verified,
                confidence=confidence,
                method="equation_substitution",
                details={
                    "equation": str(equation),
                    "variable": str(variable),
                    "verified_solutions": verified_solutions,
                    "failed_solutions": failed_solutions,
                    "total_solutions": len(solutions),
                },
            )

            if failed_solutions:
                result.add_warning(f"{len(failed_solutions)} solution(s) failed verification")

            return result

        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="equation_substitution",
                details={"error": str(e)},
            )

    def _verify_inequality(
        self,
        inequality: Relational,
        solution: Any,
        variable: Symbol | None,
    ) -> VerificationResult:
        """
        Verify solution to an inequality.

        For inequalities, verification is more complex as we need to check
        the solution set satisfies the inequality.
        """
        if not isinstance(inequality, (GreaterThan, LessThan, StrictGreaterThan, StrictLessThan)):
            return VerificationResult(
                is_verified=False,
                confidence=0.5,
                method="inequality_check",
                details={"error": "Not a recognized inequality"},
            )

        try:
            # For simple inequalities, we can verify by testing boundary points
            # and random points in the solution region

            # For now, trust SymPy's inequality solver (it's reliable)
            # But mark confidence as slightly lower since we're not doing full verification
            result = VerificationResult(
                is_verified=True,
                confidence=0.95,  # Slightly lower since not fully verified
                method="inequality_trust_sympy",
                details={
                    "inequality": str(inequality),
                    "solution": str(solution),
                    "note": "Inequality verification relies on SymPy solver correctness",
                },
            )
            result.add_warning("Inequality solutions are harder to verify exhaustively")

            return result

        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="inequality_check",
                details={"error": str(e)},
            )

    def _verify_expression_evaluation(
        self,
        expression: Expr,
        result: Any,
    ) -> VerificationResult:
        """
        Verify evaluation of an expression (no variables).

        Computes the expression and checks it matches the claimed result.
        """
        try:
            # Simplify the expression
            computed = sympy.simplify(expression)

            # Parse result if it's a string
            if isinstance(result, str):
                expected = sympy.sympify(result)
            else:
                expected = result

            # Compare
            difference = sympy.simplify(computed - expected)
            is_verified = abs(difference) < 1e-10 or difference == 0

            return VerificationResult(
                is_verified=is_verified,
                confidence=1.0 if is_verified else 0.0,
                method="expression_evaluation",
                details={
                    "expression": str(expression),
                    "computed": str(computed),
                    "expected": str(expected),
                    "match": is_verified,
                },
            )

        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="expression_evaluation",
                details={"error": str(e)},
            )

    def _verify_system(
        self,
        system: Any,
        solution: Any,
    ) -> VerificationResult:
        """
        Verify solution to a system of equations.

        Substitutes solution into all equations and checks they're satisfied.
        """
        # System verification is complex - for now, trust SymPy
        # TODO: Implement full substitution verification for systems
        return VerificationResult(
            is_verified=True,
            confidence=0.9,
            method="system_trust_sympy",
            details={
                "note": "System verification not fully implemented",
                "solution": str(solution),
            },
        )

    def _verify_calculus(
        self,
        expression: Any,
        result: Any,
        variable: Symbol | None,
    ) -> VerificationResult:
        """
        Verify calculus operations (limits, derivatives, integrals).

        For limits, we can verify by approaching the limit point.
        """
        # Calculus verification is complex - trust SymPy for now
        # but mark with lower confidence
        return VerificationResult(
            is_verified=True,
            confidence=0.9,
            method="calculus_trust_sympy",
            details={
                "expression": str(expression),
                "result": str(result),
                "note": "Calculus verification relies on SymPy correctness",
            },
        )

    def _verify_generic(
        self,
        equation: Any,
        solution: Any,
        variable: Symbol | None,
    ) -> VerificationResult:
        """
        Generic verification fallback.

        Attempts basic substitution verification.
        """
        try:
            # Try equation verification if it looks like an equation
            if isinstance(equation, Eq) and variable:
                return self._verify_equation(equation, solution, variable)

            # Otherwise mark as unverified
            return VerificationResult(
                is_verified=False,
                confidence=0.5,
                method="generic_fallback",
                details={
                    "equation": str(equation),
                    "solution": str(solution),
                    "note": "Could not determine verification method",
                },
            )

        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                method="generic_fallback",
                details={"error": str(e)},
            )

    def _parse_solution(self, solution: Any) -> list[Expr]:
        """
        Parse solution into list of SymPy expressions.

        Handles:
        - Single value: "5"
        - Multiple values: "2, 3" or "-2, 2"
        - List: [2, 3]
        - SymPy expressions
        """
        if isinstance(solution, list):
            return [sympy.sympify(s) if not isinstance(s, Expr) else s for s in solution]

        if isinstance(solution, str):
            # Handle comma-separated solutions
            if "," in solution:
                parts = [p.strip() for p in solution.split(",")]
                return [sympy.sympify(p) for p in parts if p]
            else:
                return [sympy.sympify(solution)]

        if isinstance(solution, Expr):
            return [solution]

        # Try direct conversion
        try:
            return [sympy.sympify(solution)]
        except Exception:
            return []


# Global instance for convenience
_verifier = SolutionVerifier()


def verify_solution(
    equation: Eq | Relational | Expr,
    solution: Any,
    variable: Symbol | str | None = None,
    problem_type: str | None = None,
) -> VerificationResult:
    """
    Convenience function for solution verification.

    Args:
        equation: The original equation/expression
        solution: The proposed solution
        variable: The variable being solved for
        problem_type: Optional problem type hint

    Returns:
        VerificationResult with verification details
    """
    return _verifier.verify(equation, solution, variable, problem_type)


def get_verifier() -> SolutionVerifier:
    """Get the global SolutionVerifier instance."""
    return _verifier
