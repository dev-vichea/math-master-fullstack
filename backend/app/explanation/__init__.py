"""
Explanation Layer - Generate bilingual mathematical explanations.

100% deterministic, template-based explanations without LLMs.

Features:
- Bilingual templates (Khmer/English)
- Operation-specific explanations
- Proper Khmer number formatting
- Context-aware template selection

Refactored from app/core/localization/ for better organization.
"""

from app.explanation.engine import ExplanationEngine, get_explanation_engine
from app.explanation.templates.templates import (
    ExplanationGenerator,
    NumberFormatter,
    generate_bilingual_step,
    get_explanation_generator,
)

__all__ = [
    "ExplanationGenerator",
    "get_explanation_generator",
    "generate_bilingual_step",
    "NumberFormatter",
    "ExplanationEngine",
    "get_explanation_engine",
]
