"""
Parser Layer - Mathematical expression and text parsing.

This module handles:
- Math parsing (converting text to SymPy expressions)
- Khmer text normalization (digits, punctuation)
- Exercise structure parsing (Exercise 1: a) b) c))
- Unified normalization pipeline

Refactored from app/core/parser/, app/core/khmer/, app/core/normalization/ for better organization.
"""

from app.parser.exercise_parser.exercise_parser import ParsedExercise, parse_exercise
from app.parser.expression_parser.khmer_normalizer import normalize_khmer_text
from app.parser.math_parser.expression_parser import ParsedMath, parse_math_text
from app.parser.pipeline import NormalizationPipeline, NormalizationResult

__all__ = [
    "parse_math_text",
    "ParsedMath",
    "parse_exercise",
    "ParsedExercise",
    "normalize_khmer_text",
    "NormalizationPipeline",
    "NormalizationResult",
]
