"""
Language definitions, context management, detection, and normalization for Khmer and English.

This module provides the core language abstraction for the Math Lab application,
supporting bilingual operations across Khmer (km) and English (en).
"""

from __future__ import annotations

import contextvars
import re
from contextlib import contextmanager
from enum import Enum
from typing import Any, Generator, Literal

# Supported language codes
class Language(str, Enum):
    """Supported language codes in Math Lab."""

    KM = "km"
    EN = "en"

    # Convenient aliases
    KHMER = "km"
    ENGLISH = "en"

    @property
    def code(self) -> str:
        return self.value

    @property
    def label(self) -> str:
        return "ភាសាខ្មែរ" if self == Language.KM else "English"

    @property
    def english_name(self) -> str:
        return "Khmer" if self == Language.KM else "English"


SupportedLanguage = Literal["km", "en"]

DEFAULT_LANGUAGE: Language = Language.KM
FALLBACK_LANGUAGE: Language = Language.EN

SUPPORTED_LANGUAGES: list[Language] = [Language.KM, Language.EN]

LANGUAGE_INFO: dict[Language, dict[str, Any]] = {
    Language.KM: {
        "code": "km",
        "name": "Khmer",
        "native_name": "ភាសាខ្មែរ",
        "direction": "ltr",
        "digits": "០១២៣៤៥៦៧៨៩",
        "locale": "km_KH",
        "is_default": True,
    },
    Language.EN: {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "direction": "ltr",
        "digits": "0123456789",
        "locale": "en_US",
        "is_default": False,
    },
}

# ContextVar for request-scoped language tracking
_current_language_var: contextvars.ContextVar[Language] = contextvars.ContextVar(
    "current_language", default=DEFAULT_LANGUAGE
)


def get_current_language() -> Language:
    """Return the active language for the current context/request."""
    return _current_language_var.get()


def set_current_language(lang: str | Language | None) -> Language:
    """Set the active language for the current context/request."""
    normalized = normalize_language(lang)
    _current_language_var.set(normalized)
    return normalized


@contextmanager
def use_language(lang: str | Language) -> Generator[Language, None, None]:
    """
    Context manager to temporarily override the active language.

    Example:
        >>> with use_language("en"):
        ...     print(t("status.success"))  # 'Success'
    """
    normalized = normalize_language(lang)
    token = _current_language_var.set(normalized)
    try:
        yield normalized
    finally:
        _current_language_var.reset(token)


# Unicode patterns for script detection
# U+1780 - U+17FF: Khmer
# U+19E0 - U+19FF: Khmer Symbols
_KHMER_CHAR_PATTERN = re.compile(r"[\u1780-\u17ff\u19e0-\u19ff]")
_LATIN_WORD_PATTERN = re.compile(r"\b[a-zA-Z]{2,}\b")
_MATH_OPERATORS_PATTERN = re.compile(r"[=+\-*/^()\[\]{}<≤>≥\\_]")


def normalize_language(lang: str | Language | None) -> Language:
    """
    Normalize any language string/enum to a canonical Language enum.

    Handles:
        - "km", "kh", "khm", "khmer", "ភាសាខ្មែរ" -> Language.KM
        - "en", "eng", "english", "អង់គ្លេស" -> Language.EN
        - None / unrecognized -> DEFAULT_LANGUAGE (Language.KM)
    """
    if lang is None:
        return DEFAULT_LANGUAGE

    if isinstance(lang, Language):
        return lang

    cleaned = str(lang).strip().lower()
    if cleaned in ("km", "kh", "khm", "khmer", "ភាសាខ្មែរ", "ខ្មែរ"):
        return Language.KM
    if cleaned in ("en", "eng", "english", "អង់គ្លេស"):
        return Language.EN

    return DEFAULT_LANGUAGE


def is_khmer_char(char: str) -> bool:
    """Return True if character belongs to the Khmer Unicode block."""
    if not char:
        return False
    code = ord(char[0])
    return (0x1780 <= code <= 0x17FF) or (0x19E0 <= code <= 0x19FF)


def is_khmer_text(text: str) -> bool:
    """Return True if text contains at least one Khmer character."""
    if not text:
        return False
    return bool(_KHMER_CHAR_PATTERN.search(text))


def is_english_text(text: str) -> bool:
    """Return True if text contains Latin words."""
    if not text:
        return False
    return bool(_LATIN_WORD_PATTERN.search(text))


def is_bilingual_text(text: str) -> bool:
    """Return True if text contains both Khmer and Latin/English words."""
    if not text:
        return False
    return is_khmer_text(text) and is_english_text(text)


def detect_language(text: str, default: Language | None = None) -> Language:
    """
    Automatically detect whether text is Khmer or English.

    - If text contains Khmer characters -> Language.KM
    - If text contains English words and no Khmer characters -> Language.EN
    - If ambiguous or purely numbers/symbols -> returns default or DEFAULT_LANGUAGE
    """
    if not text:
        return default or DEFAULT_LANGUAGE

    khmer_matches = _KHMER_CHAR_PATTERN.findall(text)
    if khmer_matches:
        return Language.KM

    latin_words = _LATIN_WORD_PATTERN.findall(text)
    if latin_words:
        return Language.EN

    return default or DEFAULT_LANGUAGE


def get_language_info(lang: str | Language) -> dict[str, Any]:
    """Get metadata dictionary for a language code."""
    normalized = normalize_language(lang)
    return dict(LANGUAGE_INFO.get(normalized, LANGUAGE_INFO[DEFAULT_LANGUAGE]))


__all__ = [
    "Language",
    "SupportedLanguage",
    "DEFAULT_LANGUAGE",
    "FALLBACK_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_INFO",
    "get_current_language",
    "set_current_language",
    "use_language",
    "normalize_language",
    "is_khmer_char",
    "is_khmer_text",
    "is_english_text",
    "is_bilingual_text",
    "detect_language",
    "get_language_info",
]
