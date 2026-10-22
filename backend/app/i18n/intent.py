"""
Bilingual Math Intent classification for Khmer and English.

Re-exports canonical intent classes and provides locale-aware intent
helper functions.
"""

from __future__ import annotations

from app.classifier.problem_classifier.intent_classifier import (
    IntentClassifier,
    MathIntent,
    RuleBasedIntentClassifier,
)
from app.i18n.locales import Language, normalize_language
from app.i18n.translations import translate

_global_classifier: RuleBasedIntentClassifier | None = None


def get_intent_classifier() -> RuleBasedIntentClassifier:
    """Return singleton instance of RuleBasedIntentClassifier."""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = RuleBasedIntentClassifier()
    return _global_classifier


def classify_intent(text: str) -> MathIntent:
    """Classify the mathematical intent of Khmer, English, or bilingual text."""
    classifier = get_intent_classifier()
    return classifier.classify(text)


def get_intent_display_name(
    intent: MathIntent | str,
    lang: str | Language = Language.KM,
) -> str:
    """
    Get localized human-readable display name for a MathIntent.

    Examples:
        >>> get_intent_display_name(MathIntent.SOLVE_EQUATION, "km")
        'ដោះស្រាយសមីការ'
        >>> get_intent_display_name(MathIntent.SOLVE_EQUATION, "en")
        'Solve equation'
    """
    raw_val = intent.value if isinstance(intent, MathIntent) else str(intent)
    key = f"intent.{raw_val}"
    return translate(key, lang=lang, default=raw_val)


__all__ = [
    "MathIntent",
    "IntentClassifier",
    "RuleBasedIntentClassifier",
    "get_intent_classifier",
    "classify_intent",
    "get_intent_display_name",
]
