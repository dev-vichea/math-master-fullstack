"""
Lesson-Aware Explanation Engine.

Coordinates the pipeline:
Problem → Identify Lesson/Method → Solver → Solution Steps → Explanation Template → Student-friendly Explanation

Strictly separates:
- Mathematical computation (Solver / SymPy)
- Curriculum Knowledge Base (models, registry)
- Explanation Templates (pedagogical steps: What & Why)
- Explanation Generation (filling templates with computed values)
"""

from __future__ import annotations

from typing import Any

import sympy
from sympy import Add, Mul, Poly, Symbol, factor, gcd, latex

from app.api.schemas.responses import SolutionStep
from app.explanation.templates.factorization import (
    generate_common_factor_explanation,
    generate_diff_squares_explanation,
    generate_general_factorization_explanation,
    generate_trinomial_explanation,
    get_square_root_base,
)
from app.knowledge.models import LessonMetadata
from app.knowledge.registry import get_knowledge_registry
from app.reasoning.steps.algebra.expansion import ExpansionStepGenerator


class ExplanationEngine:
    """
    Identifies curriculum method, applies explanation template, and attaches lesson metadata.
    """

    def __init__(self) -> None:
        self.registry = get_knowledge_registry()
        self.expansion_gen = ExpansionStepGenerator()

    def generate_explanation(
        self,
        expr: sympy.Expr,
        problem_type: str,
        raw_text: str = "",
        symbol: sympy.Symbol | None = None,
    ) -> tuple[list[SolutionStep], dict[str, Any] | None]:
        """
        Generates lesson-aware pedagogical solution steps and lesson metadata.

        Returns:
            (steps, lesson_info_dict)
        """
        if problem_type in ("expression_factorization", "polynomial_factorization"):
            return self._explain_factorization(expr, raw_text=raw_text, symbol=symbol)
        elif problem_type in ("factored_expression", "expression_expansion", "polynomial_expansion"):
            return self._explain_expansion(expr, raw_text=raw_text, symbol=symbol)
        elif problem_type == "calculus_limit":
            return self._explain_limit(expr, raw_text=raw_text, symbol=symbol)

        # Fallback for unhandled types
        return [], None

    def _extract_prefix(self, raw_text: str) -> str:
        """Extracts formula assignment prefix like 'A = ' or 'P = ' if present."""
        if raw_text and "=" in raw_text:
            parts = raw_text.split("=", 1)
            candidate = parts[0].strip()
            if len(candidate) <= 2 and candidate.replace("(", "").replace(")", "").isalpha():
                return f"{candidate} = "
        return ""

    def _explain_factorization(
        self,
        expr: sympy.Expr,
        raw_text: str = "",
        symbol: sympy.Symbol | None = None,
    ) -> tuple[list[SolutionStep], dict[str, Any] | None]:
        """Pedagogical factorization identifying specific method."""
        prefix = self._extract_prefix(raw_text)
        terms = expr.as_ordered_terms() if isinstance(expr, Add) else [expr]

        # 1. Method A: Common Factor Extraction
        if len(terms) >= 2:
            common = gcd(terms)
            if common != 1 and common != -1:
                method_id = "method_common_factor_extraction"
                metadata = self.registry.get_metadata(method_id)
                quotient = sympy.simplify(expr / common)
                steps = generate_common_factor_explanation(
                    expr=expr,
                    common_factor=common,
                    quotient=quotient,
                    prefix=prefix,
                )
                return steps, metadata.to_dict() if metadata else None

        # 2. Method B: Difference of Two Squares a² - b²
        if len(terms) == 2:
            t1, t2 = terms[0], terms[1]
            # Identify positive and negative terms
            pos_term = t1 if not str(t1).strip().startswith("-") else t2
            neg_term = t2 if not str(t1).strip().startswith("-") else t1
            if str(neg_term).strip().startswith("-"):
                abs_neg_term = -neg_term
            else:
                abs_neg_term = neg_term

            base_a = get_square_root_base(pos_term)
            base_b = get_square_root_base(abs_neg_term)

            if base_a is not None and base_b is not None:
                method_id = "method_diff_squares"
                metadata = self.registry.get_metadata(method_id)
                steps = generate_diff_squares_explanation(
                    expr=expr,
                    a=base_a,
                    b=base_b,
                    prefix=prefix,
                )
                return steps, metadata.to_dict() if metadata else None

        # 3. Method C: Quadratic Trinomial Split x² + bx + c
        free_syms = list(expr.free_symbols)
        if len(free_syms) == 1:
            var = free_syms[0]
            try:
                poly = Poly(expr, var)
                if poly.degree() == 2:
                    coeffs = poly.all_coeffs()
                    if len(coeffs) == 3 and coeffs[0] == 1:
                        # a = 1, b = coeffs[1], c = coeffs[2]
                        b_val = coeffs[1]
                        c_val = coeffs[2]
                        roots = sympy.roots(poly)
                        if sum(roots.values()) == 2:
                            # Two roots r1, r2 -> factors are (x - r1)(x - r2) -> p = -r1, q = -r2
                            root_list = []
                            for r, mult in roots.items():
                                root_list.extend([r] * mult)
                            p_val = -root_list[0]
                            q_val = -root_list[1]
                            if p_val.is_rational and q_val.is_rational:
                                method_id = "method_trinomial_split"
                                metadata = self.registry.get_metadata(method_id)
                                steps = generate_trinomial_explanation(
                                    expr=expr,
                                    b=b_val,
                                    c=c_val,
                                    p=p_val,
                                    q=q_val,
                                    symbol=var,
                                    prefix=prefix,
                                )
                                return steps, metadata.to_dict() if metadata else None
            except Exception:
                pass

        # 4. Fallback: General Factoring
        factored = factor(expr)
        method_id = "method_common_factor_extraction"
        metadata = self.registry.get_metadata(method_id)
        steps = generate_general_factorization_explanation(expr, factored, prefix=prefix)
        return steps, metadata.to_dict() if metadata else None

    def _explain_expansion(
        self,
        expr: sympy.Expr,
        raw_text: str = "",
        symbol: sympy.Symbol | None = None,
    ) -> tuple[list[SolutionStep], dict[str, Any] | None]:
        """Pedagogical expansion using distributive property."""
        method_id = "method_distributive_multiplication"
        metadata = self.registry.get_metadata(method_id)
        steps = self.expansion_gen.generate(expr, symbol=symbol, raw_text=raw_text)
        return steps, metadata.to_dict() if metadata else None

    def _explain_limit(
        self,
        expr: sympy.Expr,
        raw_text: str = "",
        symbol: sympy.Symbol | None = None,
    ) -> tuple[list[SolutionStep], dict[str, Any] | None]:
        """Curriculum metadata for calculus limit problem."""
        method_id = "method_limit_conjugate"
        metadata = self.registry.get_metadata(method_id)
        return [], metadata.to_dict() if metadata else None


_engine_singleton: ExplanationEngine | None = None


def get_explanation_engine() -> ExplanationEngine:
    """Returns singleton ExplanationEngine."""
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = ExplanationEngine()
    return _engine_singleton
