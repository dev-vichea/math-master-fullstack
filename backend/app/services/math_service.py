"""
Math service orchestrating the math solving pipeline:
  Khmer text -> normalize -> detect intent -> extract expression
             -> parse (SymPy) -> classify problem type -> solve + verify
             -> step-by-step (Khmer) -> SolveData
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.api.schemas.responses import SolveData
from app.classifier.problem_classifier.classifier import classify_problem
from app.classifier.problem_classifier.intent_classifier import (
    MathIntent,
    RuleBasedIntentClassifier,
)
from app.core.cache import get_solve_cache
from app.core.logging import get_logger
from app.parser.expression_parser.khmer_extractor import extract_expression
from app.parser.expression_parser.khmer_normalizer import normalize_khmer_text
from app.parser.math_parser.expression_parser import ExpressionParseError, parse_math_text
from app.solvers import solve
from app.utils.exceptions import MathProcessingError

logger = get_logger("app.services.math")

# Re-export MathProcessingError for backward compatibility
__all__ = ["MathProcessingError", "MathService", "get_math_service", "process_question"]


class MathService:
    """Service encapsulating math parsing, classification, and solving logic."""

    def __init__(self, intent_classifier: RuleBasedIntentClassifier | None = None) -> None:
        self.intent_classifier = intent_classifier or RuleBasedIntentClassifier()

    def parse_question(self, question: str) -> dict[str, Any]:
        """
        Parses question text, detects intent, extracts raw and normalized math expressions,
        and classifies the problem type without solving.
        """
        normalized_text = normalize_khmer_text(question)
        intent = self.intent_classifier.classify(normalized_text)
        raw_expression = extract_expression(normalized_text)

        if raw_expression is None:
            raise MathProcessingError("No math expression detected.")

        try:
            parsed = parse_math_text(raw_expression)
        except ExpressionParseError as exc:
            raise MathProcessingError(str(exc)) from exc

        problem_type = classify_problem(parsed)

        return {
            "detected_intent": intent.value,
            "raw_expression": raw_expression,
            "normalized_expression": str(parsed.sympy_expr),
            "problem_type": problem_type,
        }

    def process_question(self, question: str) -> SolveData:
        """
        Runs the full end-to-end math pipeline to solve and produce step-by-step output.
        """
        normalized_text = normalize_khmer_text(question)
        intent = self.intent_classifier.classify(normalized_text)

        if intent == MathIntent.UNKNOWN:
            raise MathProcessingError("Could not detect a math request in the given text.")

        raw_expression = extract_expression(normalized_text)
        if raw_expression is None:
            raise MathProcessingError("Could not find a mathematical expression in the given text.")

        try:
            parsed = parse_math_text(raw_expression)
        except ExpressionParseError as exc:
            raise MathProcessingError(str(exc)) from exc

        problem_type = classify_problem(parsed)

        # Context-aware refinement based on question phrasing
        q_lower = normalized_text.lower()
        if any(kw in q_lower for kw in ["ដាក់ជាផលគុណកត្តា", "ផលគុណកត្តា", "factor", "factorize"]):
            if problem_type in (
                "algebraic_expression",
                "arithmetic_expression",
                "expression_simplification",
                "factored_expression",
            ):
                problem_type = "expression_factorization"
        elif any(kw in q_lower for kw in ["ពន្លាត", "expand"]):
            if problem_type in ("algebraic_expression", "factored_expression"):
                problem_type = "expression_expansion"
        elif any(kw in q_lower for kw in ["ឌីផេរ៉ង់ស្យែល", "differential"]):
            problem_type = "calculus_differential_equation"
        elif any(kw in q_lower for kw in ["ដេរីវេ", "derivative", "differentiate", "derive"]):
            problem_type = "calculus_derivative"
        elif any(kw in q_lower for kw in ["រួម ឬរីក", "រួមឬរីក", "ភាពរួម", "ស្វ៊ីតរួម", "ស្វ៊ីតរីក"]):
            problem_type = "sequence_convergence"
        elif any(kw in q_lower for kw in ["ស្វ៊ីត", "ស្វិត", "sequence"]):
            if problem_type not in ("sequence_recurrence", "sequence_convergence"):
                if "lim" in raw_expression.lower() or "លីមីត" in q_lower:
                    problem_type = "sequence_limit"
                else:
                    problem_type = "sequence"

        # Check cache before solving

        cache = get_solve_cache()
        cache_key_expr = f"{raw_expression}::{problem_type}"
        result = cache.get(cache_key_expr, problem_type)
        if result is not None:
            logger.debug(f"Cache hit for '{raw_expression}' ({problem_type})")
        else:
            result = solve(parsed, problem_type)
            cache.put(cache_key_expr, result, problem_type)

        solve_data = SolveData(
            problem_type=problem_type,
            original_question=question,
            detected_intent=intent.value,
            normalized_expression=str(parsed.sympy_expr),
            variable=result.variable,
            answer=result.answer,
            is_verified=result.is_verified,
            steps=result.steps,
            lesson_info=result.lesson_info or result.metadata.get("lesson_info"),
        )
        return solve_data


@lru_cache
def get_math_service() -> MathService:
    """FastAPI dependency yielding a singleton MathService instance."""
    return MathService()


# Backward compatibility standalone function
def process_question(question: str) -> SolveData:
    return get_math_service().process_question(question)
