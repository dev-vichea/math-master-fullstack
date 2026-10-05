"""
System of equations solver.
"""

from __future__ import annotations

import sympy
from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class SystemSolver(BaseSolver):
    """
    Solves systems of linear and algebraic equations.

    Handles:
    - 2x2 systems: two equations, two unknowns
    - 3x3 systems: three equations, three unknowns
    - General equation systems
    """

    SUPPORTED_TYPES = {
        "system_linear_2x2",
        "system_linear_3x3",
        "system_equations",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve a system of equations using SymPy and generate step-by-step Khmer explanations.
        """
        expr = parsed.sympy_expr
        if isinstance(expr, (sympy.Tuple, tuple, list)):
            equations = list(expr)
        elif isinstance(expr, sympy.Eq):
            equations = [expr]
        else:
            equations = []

        symbols = sorted(parsed.symbols, key=lambda s: s.name)
        if not equations or not symbols:
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="មិនអាចវិភាគប្រព័ន្ធសមីការបានទេ",
                        description_en="Could not analyze system of equations",
                        expression=str(parsed.raw_text),
                    )
                ],
                metadata={"problem_type": problem_type},
            )

        try:
            sols = sympy.solve(equations, symbols, dict=True)
            if not sols:
                return SolveResult(
                    answer=r"\text{គ្មានចម្លើយ (No solution)}",
                    variable=str(symbols[0]) if symbols else "x",
                    is_verified=True,
                    steps=[
                        SolutionStep(
                            order=1,
                            description_km="ពិនិត្យប្រព័ន្ធសមីការ៖ គ្មានដំណោះស្រាយរួមទេ (ប្រព័ន្ធមិនចុះសម្រុង) ។",
                            description_en="Check system of equations: No common solution exists (inconsistent system).",
                            expression=r"\emptyset",
                            title_km="ពិនិត្យលទ្ធភាពចម្លើយ",
                            title_en="Check Solution Feasibility",
                        )
                    ],
                    metadata={"problem_type": problem_type},
                )

            first_sol = sols[0]
            ans_parts = [f"{s} = {sympy.latex(first_sol[s])}" for s in symbols if s in first_sol]
            ans_str = ", \\quad ".join(ans_parts) if ans_parts else str(first_sol)

            # Step 1: Write down system
            eqs_latex = r" \quad \text{និង} \quad ".join(
                [f"{sympy.latex(e.lhs)} = {sympy.latex(e.rhs)}" for e in equations if isinstance(e, sympy.Eq)]
            )
            tuple_vars = f"({', '.join(str(s) for s in symbols)})"
            tuple_vals = f"({', '.join(sympy.latex(first_sol[s]) for s in symbols if s in first_sol)})"

            steps = [
                SolutionStep(
                    order=1,
                    description_km=f"គេមានប្រព័ន្ធសមីការ៖\n$${eqs_latex}$$",
                    description_en=f"Given the system of equations:\n$${eqs_latex}$$",
                    expression=eqs_latex,
                    title_km="ប្រព័ន្ធសមីការដើម",
                    title_en="Original System of Equations",
                ),
                SolutionStep(
                    order=2,
                    description_km=f"ដោះស្រាយតាមវិធីជំនួស ឬបំបាត់មេគុណ គេទាញបាន៖\n$${ans_str}$$",
                    description_en=f"Solving by substitution or elimination yields:\n$${ans_str}$$",
                    expression=ans_str,
                    title_km="ដំណោះស្រាយប្រព័ន្ធសមីការ",
                    title_en="System Solution",
                ),
                SolutionStep(
                    order=3,
                    description_km=f"ដូចនេះ គូចម្លើយនៃប្រព័ន្ធសមីការគឺ ${tuple_vars} = {tuple_vals}$ ។",
                    description_en=f"Therefore, the solution pair of the system is ${tuple_vars} = {tuple_vals}$.",
                    expression=f"{tuple_vars} = {tuple_vals}",
                    title_km="សន្និដ្ឋានចម្លើយ",
                    title_en="Final Conclusion",
                ),
            ]

            return SolveResult(
                answer=ans_str,
                variable=", ".join(str(s) for s in symbols),
                is_verified=True,
                steps=steps,
                metadata={
                    "problem_type": problem_type,
                    "solutions": [{str(k): str(v) for k, v in s_item.items()} for s_item in sols],
                },
            )
        except Exception as exc:
            return SolveResult(
                answer=None,
                variable=", ".join(str(s) for s in symbols),
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km=f"បរាជ័យក្នុងការដោះស្រាយប្រព័ន្ធសមីការ៖ {exc}",
                        description_en=f"Failed to solve system of equations: {exc}",
                        expression=str(parsed.raw_text),
                    )
                ],
                metadata={"error": str(exc), "problem_type": problem_type},
            )
