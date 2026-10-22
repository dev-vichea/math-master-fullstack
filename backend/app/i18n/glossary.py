"""
Mathematical Terminology and Glossary Translation for Khmer and English.

Bridges the BacII & CSCA mathematical glossary (CHEANG SOKKONG / EDU-IKH)
to provide high-speed two-way term translation, command word mappings,
and categorized vocabulary search.
"""

from __future__ import annotations

from typing import Any

from app.i18n.locales import Language, normalize_language
from app.knowledge.bilingual_glossary import (
    ALL_MATH_TERMS,
    COMMAND_WORDS,
    STRUCTURED_ENTRIES,
    GlossaryEntry,
    get_all_categories,
    lookup_english,
    lookup_khmer,
    search_glossary,
)


def translate_math_term(
    term: str,
    target_lang: str | Language = Language.KM,
) -> str | None:
    """
    Translate a mathematical term between Khmer and English.

    Args:
        term: Term in either English or Khmer
        target_lang: Desired target language (Language.KM or Language.EN)

    Returns:
        Translated term string or None if not found.

    Examples:
        >>> translate_math_term("derivative", "km")
        'ដេរីវេ'
        >>> translate_math_term("ដេរីវេ", "en")
        'derivative'
    """
    if not term:
        return None

    lang = normalize_language(target_lang)
    clean_term = term.strip()

    if lang == Language.KM:
        # English -> Khmer lookup
        result = lookup_khmer(clean_term)
        if result:
            return result
        # Check command words
        return COMMAND_WORDS.get(clean_term.lower())
    else:
        # Prioritize exact matches over loose substring matches
        for en, km in ALL_MATH_TERMS.items():
            parts = [p.strip() for p in km.split("/")]
            if clean_term == km.strip() or clean_term in parts:
                return en

        result = lookup_english(clean_term)
        if result:
            return result
        # Reverse lookup in command words
        for en_cmd, km_cmd in COMMAND_WORDS.items():
            if clean_term in km_cmd or km_cmd in clean_term:
                return en_cmd
        return None


def get_bilingual_term(term: str) -> dict[str, str] | None:
    """
    Given a term in either Khmer or English, return both language versions.

    Returns:
        {"km": "...", "en": "..."} or None if term is unknown.
    """
    if not term:
        return None

    clean = term.strip()
    km_trans = lookup_khmer(clean)
    if km_trans:
        return {"km": km_trans, "en": clean}

    en_trans = lookup_english(clean)
    if en_trans:
        return {"km": clean, "en": en_trans}

    return None


def get_command_words(lang: str | Language = Language.KM) -> dict[str, str]:
    """
    Return math exercise command words mapped for the requested language.
    If lang is 'km', returns {english: khmer}.
    If lang is 'en', returns {khmer: english}.
    """
    target_lang = normalize_language(lang)
    if target_lang == Language.KM:
        return dict(COMMAND_WORDS)
    return {km: en for en, km in COMMAND_WORDS.items()}


def search_math_terms(
    query: str = "",
    category: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search glossary entries matching query and optional category filter.
    """
    entries = search_glossary(query=query, category=category)
    return [e.to_dict() for e in entries]


def get_categories() -> list[str]:
    """Return all unique mathematical domains in the glossary."""
    return get_all_categories()


__all__ = [
    "ALL_MATH_TERMS",
    "COMMAND_WORDS",
    "GlossaryEntry",
    "translate_math_term",
    "get_bilingual_term",
    "get_command_words",
    "search_math_terms",
    "get_categories",
    "lookup_khmer",
    "lookup_english",
]
