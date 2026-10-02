"""
Step-by-step reasoning for Logarithmic Expression Evaluation and Properties.
(e.g., e^{ln 7} = 7, ln(e^{x-2}) = x - 2, ln(e^{7x}) = 7x).

Designed for Grade 12 / Cambodian BacII National Examination:
- Rule: e^{\ln a} = a  (for a > 0)
- Rule: \ln(e^u) = u   (for any real expression u)
- Rule: \ln(e) = 1, \ln(1) = 0
- Rule: \ln(a^n) = n \ln(a)
- Rule: \ln(a/b) = \ln(a) - \ln(b)
- Rule: \ln(ab) = \ln(a) + \ln(b)
"""

from __future__ import annotations

import re
from typing import Any

import sympy
from sympy import Symbol, exp, latex, log

from app.api.schemas.responses import SolutionStep
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
    # Clean up redundant multiplication artifacts
    text = re.sub(r"\b1\s*\\cdot\s*", "", text)
    text = re.sub(r"(?<![0-9a-zA-Z])1\s*\\frac", r"\\frac", text)
    text = re.sub(r"\\left\(-1\\right\)\s*(\d+)", r"-\1", text)
    text = re.sub(r"\(-1\)\s*(\d+)", r"-\1", text)
    return text


class LogarithmStepGenerator(StepGenerator):
    """Generates pedagogical steps for evaluating and simplifying logarithmic expressions."""

    problem_type = "logarithm_evaluation"

    def generate(
        self,
        expr: Any,
        symbol: Symbol | None = None,
        expected_rhs: Any = None,
        raw_text: str | None = None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []

        # Convert symbol assumptions to real if needed
        real_subs = {s: Symbol(s.name, real=True) for s in expr.free_symbols}
        simplified = expr.subs(real_subs).simplify() if hasattr(expr, "subs") else expr

        raw_str = raw_text or _to_latex(expr)

        # ------------------------------------------------------------------
        # Case 1: e^{\ln a} (e.g., e^{\ln 7})
        # ------------------------------------------------------------------
        if (
            isinstance(expr, sympy.Pow)
            and (expr.base == sympy.E or expr.base.name in ("e", r"\mathrm{e}"))
            and isinstance(expr.exp, log)
        ) or (raw_text and ("e^{\\ln" in raw_text or "e^\\ln" in raw_text or "e^{ln" in raw_text)):
            arg = expr.exp.args[0] if isinstance(getattr(expr, "exp", None), log) else simplified
            arg_latex = _to_latex(arg)
            ans_latex = _to_latex(simplified)

            steps.append(
                SolutionStep(
                    order=1,
                    title_km="កំណត់កន្សោមដើម",
                    title_en="Identify Original Expression",
                    description_km=f"យើងមានកន្សោម ${raw_str}$។",
                    description_en=f"Given the expression ${raw_str}$.",
                    expression=f"A = {raw_str}",
                )
            )
            steps.append(
                SolutionStep(
                    order=2,
                    title_km="អនុវត្តរូបមន្តលក្ខណៈលោការីតនេពែ",
                    title_en="Apply Logarithmic Property Identity",
                    description_km=(
                        f"អនុវត្តរូបមន្តលក្ខណៈគ្រឹះ $e^{{\\ln a}} = a$ (ចំពោះ $a > 0$) "
                        f"ដែលក្នុងនោះ $a = {arg_latex}$។"
                    ),
                    description_en=(
                        f"Apply the identity $e^{{\\ln a}} = a$ (for $a > 0$) where $a = {arg_latex}$."
                    ),
                    expression=r"e^{\ln a} = a \implies e^{\ln " + arg_latex + "} = " + ans_latex,
                )
            )
            steps.append(
                SolutionStep(
                    order=3,
                    title_km="សន្និដ្ឋានតម្លៃចុងក្រោយ",
                    title_en="State Final Evaluated Value",
                    description_km=f"ដូចនេះ ${raw_str} = {ans_latex}$",
                    description_en=f"Therefore, ${raw_str} = {ans_latex}$",
                    expression=f"{raw_str} = {ans_latex}",
                )
            )
            return steps

        # ------------------------------------------------------------------
        # Case 2: \ln(e^u) (e.g., \ln(e^{x-2}), \ln(e^{7x}))
        # ------------------------------------------------------------------
        has_log_exp = False
        inner_power = None
        if isinstance(expr, log):
            arg = expr.args[0]
            if isinstance(arg, exp) or (
                isinstance(arg, sympy.Pow)
                and (arg.base == sympy.E or getattr(arg.base, "name", "") in ("e", r"\mathrm{e}"))
            ):
                has_log_exp = True
                inner_power = arg.exp if isinstance(arg, exp) else arg.exp
        elif raw_text and ("\\ln e^" in raw_text or "\\ln(e^" in raw_text or "ln e^" in raw_text):
            has_log_exp = True
            inner_power = simplified

        if has_log_exp and inner_power is not None:
            power_latex = _to_latex(inner_power)
            ans_latex = _to_latex(simplified)

            steps.append(
                SolutionStep(
                    order=1,
                    title_km="កំណត់កន្សោមដើម",
                    title_en="Identify Original Expression",
                    description_km=f"យើងមានកន្សោម ${raw_str}$។",
                    description_en=f"Given the expression ${raw_str}$.",
                    expression=f"A = {raw_str}",
                )
            )
            steps.append(
                SolutionStep(
                    order=2,
                    title_km="អនុវត្តរូបមន្តលក្ខណៈលោការីតនេពែ",
                    title_en="Apply Logarithmic Property Identity",
                    description_km=(
                        f"អនុវត្តរូបមន្តលក្ខណៈ $\\ln(e^u) = u$ (ចំពោះគ្រប់កន្សោម $u$) "
                        f"ដែលក្នុងនោះ $u = {power_latex}$។"
                    ),
                    description_en=(
                        f"Apply the identity $\\ln(e^u) = u$ where $u = {power_latex}$."
                    ),
                    expression=rf"\ln(e^u) = u \implies \ln(e^{{{power_latex}}}) = {ans_latex}",
                )
            )
            steps.append(
                SolutionStep(
                    order=3,
                    title_km="សន្និដ្ឋានតម្លៃចុងក្រោយ",
                    title_en="State Final Evaluated Value",
                    description_km=f"ដូចនេះ ${raw_str} = {ans_latex}$",
                    description_en=f"Therefore, ${raw_str} = {ans_latex}$",
                    expression=f"{raw_str} = {ans_latex}",
                )
            )
            return steps

        # ------------------------------------------------------------------
        # Case 3: General logarithmic evaluation / simplification
        # ------------------------------------------------------------------
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់កន្សោមដើម",
                title_en="Identify Original Expression",
                description_km=f"យើងមានកន្សោម ${_to_latex(expr)}$។",
                description_en=f"Given the expression ${_to_latex(expr)}$.",
                expression=f"A = {_to_latex(expr)}",
            )
        )
        steps.append(
            SolutionStep(
                order=2,
                title_km="អនុវត្តរូបមន្តលក្ខណៈលោការីតនេពែ",
                title_en="Apply Natural Logarithm Rules",
                description_km="អនុវត្តរូបមន្ត និងលក្ខណៈនៃអនុគមន៍លោការីតនេពែដើម្បីគណនា និងសម្រួលកន្សោម។",
                description_en="Apply natural logarithm identities to evaluate and simplify the expression.",
                expression=f"= {_to_latex(simplified)}",
            )
        )
        steps.append(
            SolutionStep(
                order=3,
                title_km="សន្និដ្ឋានតម្លៃចុងក្រោយ",
                title_en="State Final Evaluated Value",
                description_km=f"ដូចនេះ ${_to_latex(expr)} = {_to_latex(simplified)}$",
                description_en=f"Therefore, ${_to_latex(expr)} = {_to_latex(simplified)}$",
                expression=f"{_to_latex(expr)} = {_to_latex(simplified)}",
            )
        )
        return steps
