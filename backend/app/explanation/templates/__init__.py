"""
Explanation Templates - Bilingual mathematical explanation templates.

Template-based system for:
- Arithmetic operations (add, subtract, multiply, divide)
- Algebraic operations (move_term, combine_like_terms, factor, expand)
- Equation solving (isolate_variable, substitute)
- Quadratic operations (quadratic_formula, complete_square)
- Special operations (simplify, verify, final_answer)

All templates support Khmer and English with proper number formatting.
"""

from app.explanation.templates.templates import (
    ExplanationGenerator,
    NumberFormatter,
    generate_bilingual_step,
    get_explanation_generator,
)

__all__ = [
    "ExplanationGenerator",
    "NumberFormatter",
    "get_explanation_generator",
    "generate_bilingual_step",
]
