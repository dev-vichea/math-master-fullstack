"""
Khmer text processing for mathematical expressions.

DEPRECATED: Components have been moved to:
- app.parser.expression_parser (normalization, digits)
- app.parser.exercise_parser (exercise parsing)
- app.classifier.problem_classifier (intent classification)

Backward compatibility maintained for now.
"""

import warnings

from app.classifier.problem_classifier.intent_classifier import (
    MathIntent,
    RuleBasedIntentClassifier,
)
from app.parser.expression_parser.digits import khmer_digits_to_arabic
from app.parser.expression_parser.khmer_normalizer import normalize_khmer_text

warnings.warn(
    "app.core.khmer is deprecated. Components moved to app.parser and app.classifier.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "normalize_khmer_text",
    "khmer_digits_to_arabic",
    "MathIntent",
    "RuleBasedIntentClassifier",
]
