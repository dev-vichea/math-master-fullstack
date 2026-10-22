"""
Locales alias and re-exports for language definitions.
"""

from app.i18n.language import (
    DEFAULT_LANGUAGE,
    FALLBACK_LANGUAGE,
    LANGUAGE_INFO,
    SUPPORTED_LANGUAGES,
    Language,
    SupportedLanguage,
    detect_language,
    get_current_language,
    get_language_info,
    is_bilingual_text,
    is_english_text,
    is_khmer_char,
    is_khmer_text,
    normalize_language,
    set_current_language,
    use_language,
)

SupportedLocale = SupportedLanguage
LANGUAGE_METADATA = LANGUAGE_INFO

__all__ = [
    "Language",
    "SupportedLanguage",
    "SupportedLocale",
    "DEFAULT_LANGUAGE",
    "FALLBACK_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_INFO",
    "LANGUAGE_METADATA",
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
