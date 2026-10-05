"""
OCR normalization package.

Consolidated normalization system for math text.
"""

from app.ocr.normalization.canonical_normalizer import (
    NormalizationResult,
    khmer_digits_to_arabic,
    normalize_math_text,
    repair_ocr_artifacts,
    safe_normalize_math,
    sanitize_ocr_math_text,
    structural_normalize,
)

__all__ = [
    "NormalizationResult",
    "khmer_digits_to_arabic",
    "normalize_math_text",
    "repair_ocr_artifacts",
    "safe_normalize_math",
    "sanitize_ocr_math_text",
    "structural_normalize",
]
