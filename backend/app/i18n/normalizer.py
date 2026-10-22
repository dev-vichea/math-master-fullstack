"""
Bilingual text normalization and mathematical expression extraction.

Provides canonical normalization for Khmer, English, and mixed bilingual
math problem queries, standardizing digits, punctuation, percentages,
and boilerplate instruction phrases.
"""

from __future__ import annotations

import re
import unicodedata

# Re-export canonical implementations from app.parser
from app.parser.expression_parser.digits import khmer_digits_to_arabic
from app.parser.expression_parser.khmer_extractor import extract_expression
from app.parser.expression_parser.khmer_normalizer import (
    convert_percentages_to_decimals,
    normalize_khmer_text,
)

# Common English math instructional prefixes that can be stripped or normalized
_ENGLISH_PREFIX_PATTERNS = [
    r"^(?:exercise|problem|question)\s*(?:\d+|[a-zA-Z]|[ivxIVX]+)?\s*[:.-]\s*",
    r"^(?:solve\s+(?:for\s+[a-zA-Z]\s*)?(?:in|if|the\s+equation)?\s*[:.-]?\s*)",
    r"^(?:find\s+(?:the\s+value\s+of\s+)?[a-zA-Z]\s*(?:if|in)?\s*[:.-]?\s*)",
    r"^(?:evaluate|calculate|compute|simplify|expand|factorize|factor)\s*[:.-]?\s*",
    r"^(?:what\s+is\s+)",
]


def normalize_english_text(text: str) -> str:
    """
    Normalize English math instruction text.
    Standardizes dashes, minus signs, quotation marks, and collapses whitespace.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text).strip()
    # Normalize dashes and minus
    text = re.sub(r"[—–−‐]", "-", text)
    # Convert percentages to decimals
    text = convert_percentages_to_decimals(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_bilingual_text(text: str) -> str:
    """
    Normalize mixed Khmer-English math text into a unified canonical form.

    1. Unicode NFC normalization.
    2. Convert Khmer digits to Arabic numerals (e.g. ២x -> 2x).
    3. Normalize Khmer punctuation to ASCII (។ -> ., ៖ -> :).
    4. Repair common OCR typos in Khmer domain terms.
    5. Convert Khmer and English percentage expressions ("20%" or "20 ភាគរយ").
    6. Normalize dashes, minus signs, and intervals.
    7. Clean redundant whitespace.
    """
    if not text:
        return ""

    # normalize_khmer_text already carries out Unicode NFC, digit conversion,
    # punctuation mapping, OCR keyword repairs, and percentage decimals
    normalized = normalize_khmer_text(text)

    # Standardize remaining Unicode punctuation or symbols
    normalized = re.sub(r"[“”«»]", '"', normalized)
    normalized = re.sub(r"[‘’`´]", "'", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def clean_mixed_math_text(text: str) -> str:
    """
    Clean boilerplate instructional words from both Khmer and English,
    leaving the core math prompt.
    """
    normalized = normalize_bilingual_text(text)
    for pat in _ENGLISH_PREFIX_PATTERNS:
        normalized = re.sub(pat, "", normalized, flags=re.IGNORECASE).strip()
    return normalized


__all__ = [
    "khmer_digits_to_arabic",
    "normalize_khmer_text",
    "normalize_english_text",
    "normalize_bilingual_text",
    "convert_percentages_to_decimals",
    "extract_expression",
    "clean_mixed_math_text",
]
