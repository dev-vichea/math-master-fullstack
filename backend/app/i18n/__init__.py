"""
Internationalization (i18n) — Khmer and English Language Support.

Provides a clean, streamlined language framework for the Math Lab platform:
- Language enums, detection, and context switching (Khmer & English)
- Deterministic bilingual translations for messages, intents, problem types, and operations
- Text normalization for Khmer, English, and mixed bilingual prompts
- Reading and converting Khmer digits (០-៩) to standard Arabic digits (0-9)
- BacII & CSCA mathematical glossary terminology translation
- Step-by-step bilingual explanation templates

Usage:
    from app.i18n import (
        Language,
        detect_language,
        t,
        translate,
        normalize_khmer_text,
        normalize_bilingual_text,
        khmer_digits_to_arabic,
        translate_math_term,
        MathIntent,
        RuleBasedIntentClassifier,
        ExplanationGenerator,
        create_bilingual_step,
    )
"""

from __future__ import annotations

# 1. Language & Locale Core
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
from app.i18n.locales import (
    LANGUAGE_METADATA,
    SupportedLocale,
)

# 2. Translations & Message Catalog
from app.i18n.translations import (
    TRANSLATIONS,
    format_bilingual,
    get_all_translations,
    get_bilingual,
    register_translation,
    t,
    translate,
)

# 3. Text Normalization & Expression Extraction
from app.i18n.normalizer import (
    clean_mixed_math_text,
    convert_percentages_to_decimals,
    extract_expression,
    khmer_digits_to_arabic,
    normalize_bilingual_text,
    normalize_english_text,
    normalize_khmer_text,
)

# 4. Glossary & Mathematical Terminology Translation
from app.i18n.glossary import (
    ALL_MATH_TERMS,
    COMMAND_WORDS,
    GlossaryEntry,
    get_bilingual_term,
    get_categories,
    get_command_words,
    lookup_english,
    lookup_khmer,
    search_math_terms,
    translate_math_term,
)

# 5. Intent Classification
from app.i18n.intent import (
    IntentClassifier,
    MathIntent,
    RuleBasedIntentClassifier,
    classify_intent,
    get_intent_classifier,
    get_intent_display_name,
)

# 6. Bilingual Explanation Templates & Steps
from app.i18n.templates import (
    ExplanationGenerator,
    create_bilingual_step,
    generate_bilingual_step,
    get_explanation_generator,
    localize_solution_step,
)

__all__ = [
    # Language Core
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
    "detect_language",
    "is_khmer_char",
    "is_khmer_text",
    "is_english_text",
    "is_bilingual_text",
    "get_language_info",
    # Translations
    "TRANSLATIONS",
    "translate",
    "t",
    "get_bilingual",
    "format_bilingual",
    "register_translation",
    "get_all_translations",
    # Normalizer & Digit conversion
    "khmer_digits_to_arabic",
    "normalize_khmer_text",
    "normalize_english_text",
    "normalize_bilingual_text",
    "convert_percentages_to_decimals",
    "extract_expression",
    "clean_mixed_math_text",
    # Glossary
    "ALL_MATH_TERMS",
    "COMMAND_WORDS",
    "GlossaryEntry",
    "translate_math_term",
    "get_bilingual_term",
    "lookup_khmer",
    "lookup_english",
    "get_command_words",
    "search_math_terms",
    "get_categories",
    # Intent
    "MathIntent",
    "IntentClassifier",
    "RuleBasedIntentClassifier",
    "classify_intent",
    "get_intent_classifier",
    "get_intent_display_name",
    # Templates
    "ExplanationGenerator",
    "get_explanation_generator",
    "generate_bilingual_step",
    "create_bilingual_step",
    "localize_solution_step",
]
