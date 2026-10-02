"""
Expression Parser - Khmer text normalization and processing.

Handles:
- Khmer digit conversion (០-៩ → 0-9)
- Khmer punctuation normalization
- Unicode subscripts/superscripts
- Mathematical operator standardization
"""

from app.parser.expression_parser.digits import (
    arabic_digits_to_khmer,
    khmer_digits_to_arabic,
)
from app.parser.expression_parser.khmer_normalizer import normalize_khmer_text

__all__ = [
    "normalize_khmer_text",
    "khmer_digits_to_arabic",
    "arabic_digits_to_khmer",
]
