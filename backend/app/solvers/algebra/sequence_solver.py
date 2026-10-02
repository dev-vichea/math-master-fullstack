"""
Sequence Solver for Cambodian Grade 12 BacII Real Sequences (ស្វ៊ីតចំនួនពិត).

Handles:
1. Sequence Convergence & Divergence (សិក្សាភាពរួម ឬ រីកនៃស្វ៊ីត):
   - Polynomial sequences: U_n = 3n^2 + 5n + 1
   - Rational sequences: U_n = (n^2 + n) / (2n^2 + 5)
   - Radicals and inverse powers: U_n = 2 - 3/n + 4/sqrt(n)
   - Squeeze theorem sequences: U_n = sin(2n) / 5^n, U_n = n*sin(n) / (n^2 + 1)
2. Sequence Limits at Infinity (គណនាលីមីតនៃស្វ៊ីត):
   - Rational leading term factoring
   - Oscillating and bounded terms: (-1)^n, sin, cos
   - Conjugates for radical differences
   - Factorials: (n+1)! = (n+1)n!
3. Ratio Limits (គណនាផលធៀបដាឡំប៊ែរ):
   - lim_{n -> +oo} U_{n+1} / U_n
4. First-Order Linear Recurrences (ស្វ៊ីតកំណត់ដោយទំនាក់ទំនងដំណាល):
   - a_{n+1} = p * a_n + q with initial term a_1
   - Fixed point L = q / (1 - p)
   - Auxiliary geometric sequence v_n = a_n - L
   - Closed form general term a_n = L + (a_1 - L) p^{n-1}
   - Limit as n -> +oo and convergence analysis.
"""

from __future__ import annotations

import re
from typing import Any
import sympy
from sympy import Eq, Limit, Symbol, Tuple, latex, oo, S, simplify

from app.api.schemas.responses import SolutionStep
from app.knowledge.registry import get_knowledge_registry
from app.parser.math_parser.expression_parser import ParsedMath
from app.reasoning.steps.algebra.sequence import SequenceStepGenerator, _format_limit_val
from app.solvers.base import BaseSolver, SolveResult


def evaluate_sequence_limit(expr: sympy.Expr, var: Symbol) -> sympy.Expr | None:
    """
    Evaluate sequence limit as var -> +oo with domain-specific handling
    for bounded oscillating factors like (-1)^n, sin, and cos.
    """
    # 1. Direct SymPy limit
    try:
        val = Limit(expr, var, oo, dir="-").doit()
        if not (val.has(sympy.I) or "depends on" in str(val)):
            return val
    except Exception:
        pass

    # 2. Check for (-1)**var
    neg_pow = (-1) ** var
    if expr.has(neg_pow):
        try:
            val_low = Limit(expr.subs(neg_pow, -1), var, oo, dir="-").doit()
            val_high = Limit(expr.subs(neg_pow, 1), var, oo, dir="-").doit()
            if val_low == val_high and not (val_low.has(sympy.I) or "depends on" in str(val_low)):
                return val_low
            if val_low == oo and val_high == oo:
                return oo
            if val_low == -oo and val_high == -oo:
                return -oo
        except Exception:
            pass

    # 3. Check for bounded trigonometric terms sin, cos
    try:
        # Check if replacing trig functions with 0 yields a valid limit
        replaced_expr = expr.replace(
            lambda e: isinstance(e, (sympy.sin, sympy.cos)),
            lambda e: 0,
        )
        val_trig = Limit(replaced_expr, var, oo, dir="-").doit()
        if not (val_trig.has(sympy.I) or "depends on" in str(val_trig)):
            return val_trig
    except Exception:
        pass

    # 4. Fallback: try sympy.limit
    try:
        val = sympy.limit(expr, var, oo)
        if not (val.has(sympy.I) or "depends on" in str(val)):
            return val
    except Exception:
        pass

    return None


class SequenceSolver(BaseSolver):
    """
    Solver for Real Sequence problems (Grade 12 BacII).
    """

    SUPPORTED_TYPES = {
        "sequence",
        "sequence_convergence",
        "sequence_limit",
        "sequence_recurrence",
        "sequence_ratio",
        "real_sequence",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve real sequence problems and return pedagogical steps and curriculum metadata.
        """
        expr = parsed.sympy_expr
        generator = SequenceStepGenerator()
        knowledge_reg = get_knowledge_registry()

        # Route 1: Recurrence relation
        if self._is_recurrence(expr, problem_type):
            return self._solve_recurrence(expr, generator, knowledge_reg)

        # Route 2: Sequence Limit expression (Limit object)
        if self._is_limit_expr(expr):
            return self._solve_sequence_limit(expr, problem_type, generator, knowledge_reg)

        # Route 3: General Term Sequence (Eq or Expr)
        return self._solve_general_term(expr, problem_type, generator, knowledge_reg)

    # -------------------------------------------------------------------------
    # Recurrence Solver
    # -------------------------------------------------------------------------
    def _is_recurrence(self, expr: Any, problem_type: str) -> bool:
        if problem_type == "sequence_recurrence":
            return True
        if isinstance(expr, (Tuple, list, tuple)):
            return any("n+1" in str(e) or "np1" in str(e) for e in expr)
        if isinstance(expr, Eq):
            return "n+1" in str(expr.lhs) or "np1" in str(expr.lhs) or "n+1" in str(expr.rhs)
        return False

    def _solve_recurrence(
        self,
        expr: Any,
        generator: SequenceStepGenerator,
        knowledge_reg: Any,
    ) -> SolveResult:
        params = self._extract_recurrence_parameters(expr)
        if not params:
            return self._error_result("មិនអាចទាញយកសមីការដំណាលបានទេ", "Unable to extract recurrence parameters", expr)

        p, q, a1, seq_name = params
        n_sym = Symbol("n", positive=True)

        if p == 1:
            # Arithmetic progression: a_n = a_1 + (n - 1)*q
            v1 = S.Zero
            L = S.Zero
            an = a1 + (n_sym - 1) * q
            lim_val = oo if q > 0 else (-oo if q < 0 else a1)
            convergence = "convergent" if q == 0 else "divergent"
        else:
            # L = q / (1 - p)
            L = simplify(q / (1 - p))
            v1 = simplify(a1 - L)
            an = simplify(L + v1 * (p ** (n_sym - 1)))

            # Deduce limit
            if abs(p) < 1:
                lim_val = L
                convergence = "convergent"
            elif p > 1:
                if v1 > 0:
                    lim_val = oo
                elif v1 < 0:
                    lim_val = -oo
                else:
                    lim_val = L
                convergence = "divergent"
            else:
                lim_val = None
                convergence = "divergent"

        lim_str = _format_limit_val(lim_val)
        ans_str = str(lim_val) if lim_val is not None else lim_str

        # Generate detailed steps
        recurrence_info = {
            "p": p,
            "q": q,
            "a1": a1,
            "L": L,
            "v1": v1,
            "vn_formula": latex(v1 * (p ** (n_sym - 1))),
            "an_formula": latex(an),
            "seq_name": seq_name,
        }

        steps = generator.generate(
            expr,
            method_id="method_sequence_recurrence_linear",
            recurrence_info=recurrence_info,
            limit_val=lim_val,
            convergence=convergence,
        )

        method_id = "method_sequence_recurrence_linear"
        lesson_meta = knowledge_reg.get_metadata(method_id)
        lesson_info = lesson_meta.to_dict() if lesson_meta else None

        return SolveResult(
            answer=ans_str,
            variable=seq_name,
            is_verified=True,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "problem_type": "sequence_recurrence",
                "method_id": method_id,
                "fixed_point": str(L),
                "ratio": str(p),
                "initial_term": str(a1),
                "general_term": str(an),
                "limit": lim_str,
                "convergence": convergence,
            },
        )

    def _extract_recurrence_parameters(self, expr: Any) -> tuple[Any, Any, Any, str] | None:
        eqs: list[Eq] = []
        if isinstance(expr, (Tuple, list, tuple)):
            eqs = list(expr)
        elif isinstance(expr, Eq):
            eqs = [expr]
        else:
            return None

        rec_eq: Eq | None = None
        init_val: Any = S.One
        seq_name = "a"

        for eq in eqs:
            lhs_str = str(eq.lhs)
            m_init = re.search(r"^([a-zA-Z])_1$", lhs_str)
            if m_init:
                seq_name = m_init.group(1)
                init_val = eq.rhs
                continue
            if "n+1" in lhs_str or "np1" in lhs_str or "{n+1}" in lhs_str:
                rec_eq = eq

        if rec_eq is None:
            for eq in eqs:
                if "n+1" in str(eq.lhs) or "np1" in str(eq.lhs):
                    rec_eq = eq
                    break

        if rec_eq is None:
            return None

        # Determine seq_name if not already determined
        m_name = re.search(r"([a-zA-Z])_\{n\+1\}|([a-zA-Z])_np1|([a-zA-Z])_n", str(rec_eq.lhs))
        if m_name:
            seq_name = next(g for g in m_name.groups() if g)

        an_sym = None
        for s in rec_eq.rhs.free_symbols:
            if s.name in (f"{seq_name}_n", "a_n", "u_n", "v_n") or re.search(r"^[a-zA-Z]_n$", s.name):
                an_sym = s
                break
        if an_sym is None:
            syms = list(rec_eq.rhs.free_symbols)
            if syms:
                an_sym = syms[0]

        if an_sym is None:
            return None

        p = simplify(sympy.diff(rec_eq.rhs, an_sym))
        q = simplify(rec_eq.rhs.subs(an_sym, 0))
        return p, q, init_val, seq_name

    # -------------------------------------------------------------------------
    # Sequence Limit Solver (Limit object)
    # -------------------------------------------------------------------------
    def _is_limit_expr(self, expr: Any) -> bool:
        if isinstance(expr, Limit):
            return True
        if isinstance(expr, Eq) and (isinstance(expr.lhs, Limit) or isinstance(expr.rhs, Limit)):
            return True
        return False

    def _solve_sequence_limit(
        self,
        expr: Any,
        problem_type: str,
        generator: SequenceStepGenerator,
        knowledge_reg: Any,
    ) -> SolveResult:
        if isinstance(expr, Limit):
            limit_obj = expr
            seq_name = "U_n"
        elif isinstance(expr, Eq):
            limit_obj = expr.rhs if isinstance(expr.rhs, Limit) else expr.lhs
            seq_name = str(expr.lhs) if isinstance(expr.rhs, Limit) else str(expr.rhs)
        else:
            return self._error_result("កន្សោមមិនមែនជាលីមីតស្វ៊ីតទេ", "Expression is not a sequence limit", expr)

        f = limit_obj.args[0]
        var = limit_obj.args[1] if len(limit_obj.args) > 1 else Symbol("n", positive=True)

        lim_val = evaluate_sequence_limit(f, var)
        if lim_val is None:
            try:
                lim_val = limit_obj.doit()
            except Exception as e:
                return self._error_result(f"មិនអាចគណនាលីមីតបាន៖ {e}", f"Cannot evaluate limit: {e}", expr)

        lim_str = _format_limit_val(lim_val)
        ans_str = str(lim_val)

        # Detect Method ID
        method_id = self._detect_sequence_method(f, var)

        # Detect Squeeze info if applicable
        squeeze_info = None
        if method_id == "method_sequence_squeeze":
            squeeze_info = self._extract_squeeze_info(f, var, seq_name)

        # Generate steps
        steps = generator.generate(
            limit_obj,
            method_id=method_id,
            limit_val=lim_val,
            squeeze_info=squeeze_info,
        )

        lesson_meta = knowledge_reg.get_metadata(method_id)
        lesson_info = lesson_meta.to_dict() if lesson_meta else None

        return SolveResult(
            answer=ans_str,
            variable=str(var),
            is_verified=True,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "problem_type": "sequence_limit",
                "method_id": method_id,
                "limit": lim_str,
            },
        )

    # -------------------------------------------------------------------------
    # General Term Sequence Solver (Convergence Study)
    # -------------------------------------------------------------------------
    def _solve_general_term(
        self,
        expr: Any,
        problem_type: str,
        generator: SequenceStepGenerator,
        knowledge_reg: Any,
    ) -> SolveResult:
        if isinstance(expr, Eq):
            seq_label = str(expr.lhs)
            formula = expr.rhs
        else:
            seq_label = "U_n"
            formula = expr

        # Check if formula is a D'Alembert ratio question
        # e.g., ratio of consecutive terms or ratio limit
        var = Symbol("n", positive=True)
        for s in formula.free_symbols:
            if s.name in ("n", "k"):
                var = s
                break

        lim_val = evaluate_sequence_limit(formula, var)
        if lim_val is None:
            try:
                lim_val = Limit(formula, var, oo, dir="-").doit()
            except Exception as e:
                return self._error_result(f"មិនអាចគណនាលីមីតស្វ៊ីតបាន៖ {e}", f"Cannot evaluate sequence limit: {e}", expr)

        lim_str = _format_limit_val(lim_val)
        ans_str = str(lim_val)

        # Determine convergence
        is_finite = bool(lim_val.is_finite if hasattr(lim_val, "is_finite") else lim_val not in (oo, -oo))
        convergence = "convergent" if is_finite else "divergent"

        method_id = self._detect_sequence_method(formula, var)
        # If studying convergence/divergence
        if problem_type in ("sequence_convergence", "sequence", "real_sequence") and method_id != "method_sequence_squeeze":
            method_id = "method_sequence_convergence"

        squeeze_info = None
        if method_id == "method_sequence_squeeze":
            squeeze_info = self._extract_squeeze_info(formula, var, seq_label)

        steps = generator.generate(
            expr,
            method_id=method_id,
            limit_val=lim_val,
            convergence=convergence,
            squeeze_info=squeeze_info,
        )

        lesson_meta = knowledge_reg.get_metadata(method_id)
        lesson_info = lesson_meta.to_dict() if lesson_meta else None

        return SolveResult(
            answer=ans_str,
            variable=seq_label,
            is_verified=True,
            steps=steps,
            lesson_info=lesson_info,
            metadata={
                "problem_type": "sequence_convergence",
                "method_id": method_id,
                "limit": lim_str,
                "convergence": convergence,
            },
        )

    # -------------------------------------------------------------------------
    # Method Detection & Squeeze Info Helpers
    # -------------------------------------------------------------------------
    def _detect_sequence_method(self, f: sympy.Expr, var: Symbol) -> str:
        # 1. Factorial
        if f.has(sympy.factorial):
            return "method_sequence_factorial"

        # 2. Conjugate for radicals
        has_sqrt = any(
            isinstance(p, sympy.Pow) and p.exp == S(1)/2
            for p in f.atoms(sympy.Pow)
        )
        if has_sqrt:
            num, den = f.as_numer_denom()
            if num.has(sympy.Pow) and any(p.exp == S(1)/2 for p in num.atoms(sympy.Pow)):
                return "method_sequence_conjugate"

        # 3. Squeeze Theorem (sin, cos, (-1)^n where denominator grows to oo)
        if f.has(sympy.sin) or f.has(sympy.cos):
            # Check if it has a bounded trig factor divided by power
            num, den = f.as_numer_denom()
            if den != 1 and den.has(var):
                return "method_sequence_squeeze"

        # 4. Rational sequence
        num, den = f.as_numer_denom()
        if den != 1 and den.has(var):
            return "method_sequence_limit_rational"

        # Default
        return "method_sequence_convergence"

    def _extract_squeeze_info(self, f: sympy.Expr, var: Symbol, seq_name: str) -> dict[str, str]:
        bounded_part = r"\sin n"
        bound_expr = r"\frac{1}{n}"

        if f.has(sympy.sin):
            for atom in f.atoms(sympy.sin):
                bounded_part = latex(atom)
                break
        elif f.has(sympy.cos):
            for atom in f.atoms(sympy.cos):
                bounded_part = latex(atom)
                break

        # Calculate bound: substitute trig with 1
        bound_formula = f.replace(
            lambda e: isinstance(e, (sympy.sin, sympy.cos)),
            lambda e: 1,
        )
        bound_expr = latex(simplify(bound_formula))

        return {
            "bounded_part": bounded_part,
            "bound_expr": bound_expr,
            "seq_name": seq_name,
        }

    def _error_result(self, desc_km: str, desc_en: str, expr: Any) -> SolveResult:
        return SolveResult(
            answer=None,
            variable=None,
            is_verified=False,
            steps=[
                SolutionStep(
                    order=1,
                    description_km=desc_km,
                    description_en=desc_en,
                    expression=str(expr),
                )
            ],
            metadata={"error": desc_en},
        )
