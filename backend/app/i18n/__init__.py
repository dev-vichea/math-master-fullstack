"""
Internationalization (i18n) — Khmer/English bilingual support.

Consolidates all localization, digit mapping, text normalization,
and bilingual template utilities into a single importable package.

Re-exports from the canonical implementations in core/khmer/ and
core/localization/ for a cleaner public API.

Usage:
    from app.i18n import (
        khmer_digits_to_arabic,
        normalize_khmer_text,
        RuleBasedIntentClassifier,
        MathIntent,
        ExplanationGenerator,
    )
"""

# Khmer digit mapping
from app.core.khmer.digits import khmer_digits_to_arabic

# Khmer text extraction
from app.core.khmer.extractor import extract_expression

# Khmer intent classification
from app.core.khmer.intent import MathIntent, RuleBasedIntentClassifier

# Khmer text normalization
from app.core.khmer.normalizer import (
    convert_percentages_to_decimals,
    normalize_khmer_text,
)

# Bilingual explanation templates
from app.core.localization.templates import (
    ExplanationGenerator,
    generate_bilingual_step,
    get_explanation_generator,
)

__all__ = [
    # Digits
    "khmer_digits_to_arabic",
    # Extraction
    "extract_expression",
    # Intent
    "MathIntent",
    "RuleBasedIntentClassifier",
    # Normalization
    "normalize_khmer_text",
    "convert_percentages_to_decimals",
    # Templates
    "ExplanationGenerator",
    "generate_bilingual_step",
    "get_explanation_generator",
]
