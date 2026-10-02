"""
Pedagogical Step Generator for Real Sequences (Grade 12 BacII).

Covers:
1. Sequence Convergence and Divergence (សិក្សាភាពរួម ឬ រីកនៃស្វ៊ីត):
   - Polynomial sequences: U_n = 3n^2 + 5n + 1 -> +oo (divergent)
   - Rational sequences: U_n = (n^2 + n)/(2n^2 + 5) -> 1/2 (convergent)
   - Radical & Denominator sequences: U_n = 2 - 3/n + 4/sqrt(n) -> 2 (convergent)
2. Squeeze Theorem (ទ្រឹស្តីបទញှៀប):
   - Trigonometric sequences: U_n = sin(2n)/5^n -> 0, U_n = n*sin(n)/(n^2 + 1) -> 0
   - Oscillating sequences: (-1)^n bounds
3. Sequence Limits at Infinity (គណនាលីមីតនៃស្វ៊ីត):
   - Rational dominant terms: lim (n^2 + 3n - 1)/(8n^2 - n + 1) = 1/8
   - Oscillating terms: lim (5n^3 + (-1)^n)/(n + (-1)^n) = +oo, lim [-5n^3 + (-1)^n n^3] = -oo
   - Bounded trig with powers: lim (n^2 + sin n)/(5n^2 + cos pi n) = 1/5
   - Radicals with conjugate: lim (sqrt(n+1) - sqrt(n)) = 0, lim sqrt(n)(sqrt(n-3) - sqrt(n)) = -3/2
   - Factorials: lim [n!/((n+1)! - n!) - 2/n + 3] = 3
4. D'Alembert Ratio Limit (គណនាផលធៀប lim U_{n+1} / U_n):
   - U_n = n^3 / 2^n => lim U_{n+1}/U_n = 1/2
   - V_n = 2^n / n! => lim V_{n+1}/V_n = 0
   - Dominance: lim (2^n + n^3)/(n! + n^3) = 0
5. First-Order Linear Recurrence (ស្វ៊ីតកំណត់ដោយទំនាក់ទំនងដំណាល):
   - a_{n+1} = p a_n + q with initial term a_1
   - Fixed point L = q / (1 - p)
   - Auxiliary geometric sequence v_n = a_n - L
   - Explicit closed form a_n = L + (a_1 - L) p^{n-1}
   - Deduce limit as n -> +oo and convergence status.
"""

from __future__ import annotations

from typing import Any
import sympy
from sympy import Eq, Limit, Symbol, latex, oo, S

from app.api.schemas.responses import SolutionStep
from app.reasoning.steps.base import StepGenerator


def _format_limit_val(val: Any) -> str:
    """Format limit value for LaTeX display."""
    if val == oo or str(val) in ("oo", "+oo", "+Infinity", "Infinity"):
        return r"+\infty"
    if val == -oo or str(val) in ("-oo", "-Infinity"):
        return r"-\infty"
    if isinstance(val, (sympy.Expr, sympy.Integer, sympy.Rational)):
        return latex(val)
    return str(val)


def _to_latex(expr: Any) -> str:
    if isinstance(expr, str):
        return expr
    return latex(expr)


class SequenceStepGenerator(StepGenerator):
    """Step generator for all Grade 12 BacII Real Sequence problem types."""

    problem_type = "sequence"

    def generate(
        self,
        eq_or_expr: Any,
        symbol: Symbol | None = None,
        **kwargs: Any,
    ) -> list[SolutionStep]:
        """
        Generate pedagogical steps for sequence exercises.
        kwargs may include:
          - 'method_id': str
          - 'limit_val': Any
          - 'convergence': 'convergent' | 'divergent'
          - 'recurrence_info': dict
          - 'ratio_info': dict
          - 'squeeze_info': dict
        """
        method_id = kwargs.get("method_id", "")
        recurrence_info = kwargs.get("recurrence_info")
        ratio_info = kwargs.get("ratio_info")
        squeeze_info = kwargs.get("squeeze_info")
        limit_val = kwargs.get("limit_val")
        convergence = kwargs.get("convergence")

        # 1. Recurrence Relations
        if recurrence_info or method_id == "method_sequence_recurrence_linear":
            return self._generate_recurrence_steps(eq_or_expr, recurrence_info, limit_val, convergence)

        # 2. Ratio Limits (D'Alembert)
        if ratio_info or method_id == "method_sequence_ratio_dalembert":
            return self._generate_ratio_steps(eq_or_expr, ratio_info, limit_val)

        # 3. Squeeze Theorem
        if squeeze_info or method_id == "method_sequence_squeeze":
            return self._generate_squeeze_steps(eq_or_expr, squeeze_info, limit_val, convergence)

        # 4. Sequence Convergence / Divergence study
        if convergence or method_id == "method_sequence_convergence":
            return self._generate_convergence_steps(eq_or_expr, limit_val, convergence, method_id)

        # 5. General Sequence Limits
        return self._generate_limit_steps(eq_or_expr, limit_val, method_id)

    # -------------------------------------------------------------------------
    # Recurrence Steps
    # -------------------------------------------------------------------------
    def _generate_recurrence_steps(
        self,
        eq_or_expr: Any,
        info: dict[str, Any] | None,
        limit_val: Any,
        convergence: str | None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        p = info.get("p", S.One) if info else S.One
        q = info.get("q", S.Zero) if info else S.Zero
        a1 = info.get("a1", S.Zero) if info else S.Zero
        L = info.get("L", S.Zero) if info else S.Zero
        v1 = info.get("v1", S.Zero) if info else S.Zero
        vn_formula = info.get("vn_formula", "") if info else ""
        an_formula = info.get("an_formula", "") if info else ""
        seq_name = info.get("seq_name", "a") if info else "a"
        lim_str = _format_limit_val(limit_val)

        # Step 1: Fixed Point Equation
        p_lat = latex(p)
        q_lat = latex(q)
        L_lat = latex(L)
        a1_lat = latex(a1)
        v1_lat = latex(v1)

        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់តម្លៃថេរ L",
                title_en="Determine Fixed Point L",
                description_km=f"តាង $L$ ជាចំនួនពិតដែលផ្ទៀងផ្ទាត់សមីការ $L = {p_lat} L + {q_lat}$ នាំឱ្យ $(1 - {p_lat})L = {q_lat} \\iff L = {L_lat}$ ។",
                description_en=f"Let $L$ satisfy $L = {p_lat} L + {q_lat}$, giving $(1 - {p_lat})L = {q_lat} \\iff L = {L_lat}$.",
                expression=f"L = {p_lat}L + {q_lat} \\implies L = {L_lat}",
            )
        )

        # Step 2: Auxiliary Sequence
        steps.append(
            SolutionStep(
                order=2,
                title_km="សិក្សាស្វ៊ីតជំនួយ (v_n)",
                title_en="Study Auxiliary Sequence (v_n)",
                description_km=(
                    f"តាងស្វ៊ីតជំនួយ $v_n = {seq_name}_n - L = {seq_name}_n - {L_lat}$ ។ "
                    f"យើងបាន $v_{{n+1}} = {seq_name}_{{n+1}} - {L_lat} = ({p_lat}{seq_name}_n + {q_lat}) - {L_lat} = {p_lat}({seq_name}_n - {L_lat}) = {p_lat} v_n$ ។\n"
                    f"នាំឱ្យ $(v_n)$ ជាស្វ៊ីតធរណីមាត្រដែលមានរ៉ាស្យុង $q = {p_lat}$ និងតួទីមួយ $v_1 = {seq_name}_1 - L = {a1_lat} - ({L_lat}) = {v1_lat}$ ។"
                ),
                description_en=(
                    f"Define auxiliary sequence $v_n = {seq_name}_n - L = {seq_name}_n - {L_lat}$. "
                    f"Then $v_{{n+1}} = {p_lat} v_n$, so $(v_n)$ is a geometric progression with ratio $q = {p_lat}$ and first term $v_1 = {v1_lat}$."
                ),
                expression=f"v_{{n+1}} = {p_lat} v_n, \\quad v_1 = {v1_lat}",
            )
        )

        # Step 3: Explicit General Term
        steps.append(
            SolutionStep(
                order=3,
                title_km="រកតួទូទៅនៃស្វ៊ីត",
                title_en="Find Explicit General Terms",
                description_km=(
                    f"តួទូទៅនៃស្វ៊ីតធរណីមាត្រ $(v_n)$ គឺ $v_n = v_1 \\cdot q^{{n-1}} = {vn_formula}$ ។\n"
                    f"ទាញរកតួទូទៅនៃ $({seq_name}_n)$ គឺ ${seq_name}_n = v_n + L = {an_formula}$ ។"
                ),
                description_en=(
                    f"The general term of $(v_n)$ is $v_n = v_1 \\cdot q^{{n-1}} = {vn_formula}$. "
                    f"Therefore, ${seq_name}_n = v_n + L = {an_formula}$."
                ),
                expression=f"v_n = {vn_formula} \\implies {seq_name}_n = {an_formula}",
            )
        )

        # Step 4: Sequence Limit and Convergence Conclusion
        if convergence == "convergent":
            conv_km = f"ដូចនេះ $({seq_name}_n)$ ជាស្វ៊ីតរួមខិតទៅរក {lim_str} ។"
            conv_en = f"Therefore, $({seq_name}_n)$ is a convergent sequence converging to {lim_str}."
            desc_km = f"ដោយ $|{p_lat}| < 1$ នោះ $\\lim_{{n \\to +\\infty}} ({p_lat})^{{n-1}} = 0$ ។ យើងទាញបាន $\\lim_{{n \\to +\\infty}} {seq_name}_n = {L_lat} = {lim_str}$ ។\n{conv_km}"
            desc_en = f"Since $|{p_lat}| < 1$, $\\lim_{{n \\to +\\infty}} ({p_lat})^{{n-1}} = 0$, giving $\\lim_{{n \\to +\\infty}} {seq_name}_n = {lim_str}$. {conv_en}"
        else:
            conv_km = f"ដូចនេះ $({seq_name}_n)$ ជាស្វ៊ីតរីកខិតទៅរក {lim_str} ។"
            conv_en = f"Therefore, $({seq_name}_n)$ is a divergent sequence diverging to {lim_str}."
            desc_km = f"ដោយ ${p_lat} > 1$ នោះ $\\lim_{{n \\to +\\infty}} {seq_name}_n = {lim_str}$ ។\n{conv_km}"
            desc_en = f"Since ${p_lat} > 1$, $\\lim_{{n \\to +\\infty}} {seq_name}_n = {lim_str}$. {conv_en}"

        steps.append(
            SolutionStep(
                order=4,
                title_km="គណនាលីមីត និងសន្និដ្ឋាន",
                title_en="Compute Limit and Conclude",
                description_km=desc_km,
                description_en=desc_en,
                expression=f"\\lim_{{n \\to +\\infty}} {seq_name}_n = {lim_str}",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # Squeeze Theorem Steps
    # -------------------------------------------------------------------------
    def _generate_squeeze_steps(
        self,
        eq_or_expr: Any,
        info: dict[str, Any] | None,
        limit_val: Any,
        convergence: str | None,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        bounded_part = info.get("bounded_part", r"\sin 2n") if info else r"\sin n"
        bound_expr = info.get("bound_expr", r"\frac{1}{5^n}") if info else r"0"
        seq_name = info.get("seq_name", "U_n") if info else "U_n"
        lim_str = _format_limit_val(limit_val if limit_val is not None else 0)

        # Step 1: Bounding
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់ព្រំដែននៃកន្សោម",
                title_en="Bound the Oscillating/Trigonometric Term",
                description_km=f"គេមាន $-1 \\le {bounded_part} \\le 1$ នាំឱ្យ $-{bound_expr} \\le {seq_name} \\le {bound_expr}$ ។",
                description_en=f"We have $-1 \\le {bounded_part} \\le 1$, which gives $-{bound_expr} \\le {seq_name} \\le {bound_expr}$.",
                expression=f"-{bound_expr} \\le {seq_name} \\le {bound_expr}",
            )
        )

        # Step 2: Limit of bounds
        steps.append(
            SolutionStep(
                order=2,
                title_km="គណនាលីមីតនៃព្រំដែនសងខាង",
                title_en="Evaluate Limit of Bounds",
                description_km=f"ដោយ $\\lim_{{n \\to +\\infty}} (-{bound_expr}) = 0$ និង $\\lim_{{n \\to +\\infty}} {bound_expr} = 0$",
                description_en=f"Since $\\lim_{{n \\to +\\infty}} (-{bound_expr}) = 0$ and $\\lim_{{n \\to +\\infty}} {bound_expr} = 0$",
                expression=f"\\lim_{{n \\to +\\infty}} {bound_expr} = 0",
            )
        )

        # Step 3: Squeeze conclusion
        conv_text_km = f"ដូចនេះ $({seq_name})$ ជាស្វ៊ីតរួមខិតទៅរក {lim_str} ។"
        conv_text_en = f"Therefore, $({seq_name})$ is a convergent sequence converging to {lim_str}."

        steps.append(
            SolutionStep(
                order=3,
                title_km="អនុវត្តទ្រឹស្តីបទញှៀប និងសន្និដ្ឋាន",
                title_en="Apply Squeeze Theorem and Conclude",
                description_km=f"តាមទ្រឹស្តីបទញှៀប យើងទាញបាន $\\lim_{{n \\to +\\infty}} {seq_name} = {lim_str}$ ។\n{conv_text_km}",
                description_en=f"By the Squeeze Theorem, $\\lim_{{n \\to +\\infty}} {seq_name} = {lim_str}$. {conv_text_en}",
                expression=f"\\lim_{{n \\to +\\infty}} {seq_name} = {lim_str}",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # Ratio Steps (D'Alembert)
    # -------------------------------------------------------------------------
    def _generate_ratio_steps(
        self,
        eq_or_expr: Any,
        info: dict[str, Any] | None,
        limit_val: Any,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        u_n = info.get("u_n_str", r"\frac{n^3}{2^n}") if info else r"\frac{n^3}{2^n}"
        u_np1 = info.get("u_np1_str", r"\frac{(n+1)^3}{2^{n+1}}") if info else r"\frac{(n+1)^3}{2^{n+1}}"
        ratio_simplified = info.get("ratio_simplified", r"\frac{1}{2}\left(1 + \frac{1}{n}\right)^3") if info else ""
        lim_str = _format_limit_val(limit_val)
        seq_letter = info.get("seq_letter", "U") if info else "U"

        # Step 1: Consecutive terms
        steps.append(
            SolutionStep(
                order=1,
                title_km=f"កំណត់តួ {seq_letter}_n និង {seq_letter}_{{n+1}}",
                title_en=f"Identify Terms {seq_letter}_n and {seq_letter}_{{n+1}}",
                description_km=f"គេមាន ${seq_letter}_n = {u_n}$ និង ${seq_letter}_{{n+1}} = {u_np1}$ ។",
                description_en=f"Given ${seq_letter}_n = {u_n}$, replacing $n$ with $n+1$ yields ${seq_letter}_{{n+1}} = {u_np1}$.",
                expression=f"{seq_letter}_{{n+1}} = {u_np1}",
            )
        )

        # Step 2: Form Ratio
        steps.append(
            SolutionStep(
                order=2,
                title_km="គណនា និងសម្រួលផលធៀប",
                title_en="Form and Simplify the Ratio",
                description_km=f"គណនាផលធៀប $\\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {ratio_simplified}$ ។",
                description_en=f"Form ratio $\\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {ratio_simplified}$.",
                expression=f"\\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {ratio_simplified}",
            )
        )

        # Step 3: Compute Limit
        steps.append(
            SolutionStep(
                order=3,
                title_km="គណនាលីមីតនៃផលធៀប",
                title_en="Evaluate Limit of the Ratio",
                description_km=f"កាលណា $n \\to +\\infty$ នោះ $\\lim_{{n \\to +\\infty}} \\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {lim_str}$ ។",
                description_en=f"As $n \\to +\\infty$, $\\lim_{{n \\to +\\infty}} \\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {lim_str}$.",
                expression=f"\\lim_{{n \\to +\\infty}} \\frac{{{seq_letter}_{{n+1}}}}{{{seq_letter}_n}} = {lim_str}",
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # Convergence / Divergence Steps
    # -------------------------------------------------------------------------
    def _generate_convergence_steps(
        self,
        eq_or_expr: Any,
        limit_val: Any,
        convergence: str | None,
        method_id: str,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        lim_str = _format_limit_val(limit_val)
        expr_latex = _to_latex(eq_or_expr)
        seq_label = "U_n"
        if isinstance(eq_or_expr, Eq):
            seq_label = str(eq_or_expr.lhs)
            rhs_expr = eq_or_expr.rhs
        else:
            rhs_expr = eq_or_expr

        rhs_latex = _to_latex(rhs_expr)

        # Step 1: Limit setup
        steps.append(
            SolutionStep(
                order=1,
                title_km="កំណត់លីមីតនៃស្វ៊ីត",
                title_en="Set Up Sequence Limit",
                description_km=f"ដើម្បីសិក្សាភាពរួម ឬរីកនៃស្វ៊ីត $({seq_label})$ ត្រូវគណនា $\\lim_{{n \\to +\\infty}} {seq_label}$ :",
                description_en=f"To determine convergence or divergence of $({seq_label})$, evaluate $\\lim_{{n \\to +\\infty}} {seq_label}$:",
                expression=f"\\lim_{{n \\to +\\infty}} {seq_label} = \\lim_{{n \\to +\\infty}} \\left({rhs_latex}\\right)",
            )
        )

        # Step 2: Intermediate factorization / transformation
        if method_id == "method_sequence_limit_rational":
            desc_km = "ដាក់ស្វ័យគុណធំបំផុត $n^k$ នៃភាគយក និងភាគបែងជាកត្តារួចសម្រួល ៖"
            desc_en = "Factor the highest power $n^k$ in numerator and denominator and simplify:"
        elif method_id == "method_sequence_conjugate":
            desc_km = "គុណ និងចែកនឹងកន្សោមឆ្លាស់ដើម្បីបំបាត់រ៉ាឌីកាល់ ៖"
            desc_en = "Multiply and divide by conjugate to eliminate radicals:"
        else:
            desc_km = "គណនាតម្លៃលីមីតកាលណា $n \\to +\\infty$ ៖"
            desc_en = "Evaluate the limit as $n \\to +\\infty$:"

        steps.append(
            SolutionStep(
                order=2,
                title_km="គណនាលីមីត",
                title_en="Evaluate Limit",
                description_km=desc_km,
                description_en=desc_en,
                expression=f"\\lim_{{n \\to +\\infty}} {seq_label} = {lim_str}",
            )
        )

        # Step 3: Pedagogical conclusion
        if convergence == "convergent":
            concl_km = f"ដូចនេះ $({seq_label})$ ជាស្វ៊ីតរួមខិតទៅរក {lim_str} ។"
            concl_en = f"Therefore, $({seq_label})$ is a convergent sequence converging to {lim_str}."
        else:
            concl_km = f"ដូចនេះ $({seq_label})$ ជាស្វ៊ីតរីកខិតទៅរក {lim_str} ។"
            concl_en = f"Therefore, $({seq_label})$ is a divergent sequence diverging to {lim_str}."

        steps.append(
            SolutionStep(
                order=3,
                title_km="សន្និដ្ឋានភាពរួម ឬរីក",
                title_en="Convergence/Divergence Conclusion",
                description_km=concl_km,
                description_en=concl_en,
                expression=concl_km,
            )
        )

        return steps

    # -------------------------------------------------------------------------
    # General Sequence Limits Steps
    # -------------------------------------------------------------------------
    def _generate_limit_steps(
        self,
        eq_or_expr: Any,
        limit_val: Any,
        method_id: str,
    ) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        lim_str = _format_limit_val(limit_val)
        expr_latex = _to_latex(eq_or_expr)

        if method_id == "method_sequence_conjugate":
            steps.append(
                SolutionStep(
                    order=1,
                    title_km="គុណកន្សោមឆ្លាស់",
                    title_en="Multiply by Conjugate",
                    description_km="គុណនិងចែកកន្សោមឆ្លាស់ $(\\sqrt{A} + \\sqrt{B})$ ដើម្បីលុបរាងមិនកំណត់ $\\infty - \\infty$ ៖",
                    description_en="Multiply and divide by conjugate $(\\sqrt{A} + \\sqrt{B})$ to eliminate $\\infty - \\infty$:",
                    expression=r"(\sqrt{A} - \sqrt{B}) = \frac{A - B}{\sqrt{A} + \sqrt{B}}",
                )
            )
            steps.append(
                SolutionStep(
                    order=2,
                    title_km="សម្រួល និងគណនាលីមីត",
                    title_en="Simplify and Evaluate Limit",
                    description_km=f"កាលណា $n \\to +\\infty$ គេទាញបានលទ្ធផល ៖",
                    description_en="As $n \\to +\\infty$, we obtain:",
                    expression=f"{expr_latex} = {lim_str}",
                )
            )
        elif method_id == "method_sequence_factorial":
            steps.append(
                SolutionStep(
                    order=1,
                    title_km="សម្រួលកន្សោមហ្វាក់តូរីយ៉ែល",
                    title_en="Simplify Factorial Expression",
                    description_km=r"សម្រួលកន្សោមហ្វាក់តូរីយ៉ែលដោយអនុវត្តរូបមន្ត $(n+1)! = (n+1)n!$ នាំឱ្យ $(n+1)! - n! = n!(n+1-1) = n \cdot n!$ ៖",
                    description_en=r"Simplify the factorial expression by applying $(n+1)! = (n+1)n!$ to get $(n+1)! - n! = n!(n+1-1) = n \cdot n!$:",
                    expression=r"\frac{n!}{(n+1)! - n!} = \frac{n!}{n \cdot n!} = \frac{1}{n}",
                )
            )

            steps.append(
                SolutionStep(
                    order=2,
                    title_km="គណនាលីមីតនៃកន្សោម",
                    title_en="Evaluate Final Limit",
                    description_km=f"កាលណា $n \\to +\\infty$ នោះ $\\frac{{1}}{{n}} \\to 0$ និង $\\frac{{2}}{{n}} \\to 0$ នាំឱ្យលីមីតស្មើ {lim_str} ។",
                    description_en=f"As $n \\to +\\infty$, $\\frac{{1}}{{n}} \\to 0$ and $\\frac{{2}}{{n}} \\to 0$, giving limit {lim_str}.",
                    expression=f"{expr_latex} = {lim_str}",
                )
            )
        elif method_id == "method_sequence_limit_rational":
            steps.append(
                SolutionStep(
                    order=1,
                    title_km="ទាញស្វ័យគុណដឺក្រេខ្ពស់បំផុត",
                    title_en="Factor Leading Powers",
                    description_km="ដាក់ស្វ័យគុណធំបំផុតនៃ $n$ ជាកត្តា ឬប្រៀបធៀបដឺក្រេនៃភាគយក និងភាគបែង ៖",
                    description_en="Factor out highest powers of $n$ or compare degrees of numerator and denominator:",
                    expression=f"\\lim_{{n \\to +\\infty}} \\frac{{P(n)}}{{Q(n)}} = {lim_str}",
                )
            )
            steps.append(
                SolutionStep(
                    order=2,
                    title_km="គណនាលីមីត",
                    title_en="Compute Limit Value",
                    description_km=f"លទ្ធផលលីមីតនៃស្វ៊ីតកាលណា $n \\to +\\infty$ គឺ {lim_str} ។",
                    description_en=f"The limit of the sequence as $n \\to +\\infty$ is {lim_str}.",
                    expression=f"{expr_latex} = {lim_str}",
                )
            )
        else:
            steps.append(
                SolutionStep(
                    order=1,
                    title_km="គណនាលីមីតនៃស្វ៊ីត",
                    title_en="Evaluate Sequence Limit",
                    description_km=f"គណនាលីមីតនៃស្វ៊ីតកាលណា $n \\to +\\infty$ ៖",
                    description_en=f"Evaluate the limit of the sequence as $n \\to +\\infty$:",
                    expression=f"{expr_latex} = {lim_str}",
                )
            )

        return steps
