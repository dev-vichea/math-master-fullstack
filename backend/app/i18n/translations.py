"""
Bilingual translation dictionary and localization services for Khmer and English.

Provides typed, deterministic translations for UI messages, API errors,
mathematical intents, problem categories, algebraic operations,
and pedagogical rationales.
"""

from __future__ import annotations

from typing import Any

from app.i18n.language import (
    DEFAULT_LANGUAGE,
    FALLBACK_LANGUAGE,
    Language,
    get_current_language,
    normalize_language,
)

# Central bilingual dictionary
# Keys follow category.name hierarchy
TRANSLATIONS: dict[str, dict[str, str]] = {
    # System & App
    "app.name": {
        "km": "មន្ទីរពិសោធន៍គណិតវិទ្យា (Math Lab)",
        "en": "Khmer Math Lab",
    },
    "app.tagline": {
        "km": "ជំនួយការដោះស្រាយលំហាត់គណិតវិទ្យាខ្មែរ-អង់គ្លេសកម្រិតវិទ្យាល័យ",
        "en": "Bilingual Khmer-English Math Solver for High School & BacII",
    },
    "status.success": {
        "km": "ជោគជ័យ",
        "en": "Success",
    },
    "status.error": {
        "km": "មានបញ្ហា",
        "en": "Error",
    },
    "status.verified": {
        "km": "បានផ្ទៀងផ្ទាត់ត្រឹមត្រូវ",
        "en": "Verified successfully",
    },
    "status.unverified": {
        "km": "មិនទាន់ផ្ទៀងផ្ទាត់",
        "en": "Unverified",
    },

    # Errors & Pipeline Diagnostics
    "error.no_math_found": {
        "km": "មិនអាចរកឃើញកន្សោមគណិតវិទ្យាក្នុងសំណេរនេះទេ",
        "en": "No mathematical expression detected in the given text.",
    },
    "error.unknown_intent": {
        "km": "មិនអាចកំណត់បំណងនៃលំហាត់គណិតវិទ្យាបានទេ",
        "en": "Could not detect a math request in the given text.",
    },
    "error.invalid_syntax": {
        "km": "កន្សោមគណិតវិទ្យាមិនត្រឹមត្រូវតាមទម្រង់",
        "en": "Expression could not be parsed as valid mathematics.",
    },
    "error.unsupported_type": {
        "km": "ប្រភេទបញ្ហា '{problem_type}' មិនទាន់គាំទ្រនៅឡើយ",
        "en": "Problem type '{problem_type}' is not yet supported.",
    },
    "error.solving_failed": {
        "km": "កំហុសក្នុងការដោះស្រាយ៖ {error}",
        "en": "Error during solving: {error}",
    },
    "error.vision_empty": {
        "km": "រូបភាពទទេ ឬមិនអាចអានបាន",
        "en": "Empty image or unreadable",
    },
    "error.ocr_failed": {
        "km": "ការអានអក្សរពីរូបភាព (OCR) បរាជ័យ",
        "en": "OCR text extraction failed",
    },

    # Mathematical Intents
    "intent.solve_equation": {
        "km": "ដោះស្រាយសមីការ",
        "en": "Solve equation",
    },
    "intent.solve_differential_equation": {
        "km": "ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល",
        "en": "Solve differential equation",
    },
    "intent.evaluate_expression": {
        "km": "គណនាតម្លៃកន្សោម",
        "en": "Evaluate expression",
    },
    "intent.evaluate_integral": {
        "km": "គណនាអាំងតេក្រាល",
        "en": "Evaluate integral",
    },
    "intent.evaluate_limit": {
        "km": "គណនាលីមីត",
        "en": "Evaluate limit",
    },
    "intent.simplify_expression": {
        "km": "សម្រួលកន្សោម",
        "en": "Simplify expression",
    },
    "intent.unknown": {
        "km": "មិនស្គាល់",
        "en": "Unknown",
    },

    # Mathematical Problem Types
    "type.linear_equation": {
        "km": "សមីការដឺក្រេទី១ (លីនេអ៊ែរ)",
        "en": "Linear equation",
    },
    "type.quadratic_equation": {
        "km": "សមីការដឺក្រេទី២ (ការ៉េ)",
        "en": "Quadratic equation",
    },
    "type.polynomial_equation": {
        "km": "សមីការដឺក្រេខ្ពស់",
        "en": "Polynomial equation",
    },
    "type.system_linear_2var": {
        "km": "ប្រព័ន្ធសមីការដឺក្រេទី១ មានពីរអថេរ",
        "en": "System of linear equations (2 variables)",
    },
    "type.system_of_equations": {
        "km": "ប្រព័ន្ធសមីការ",
        "en": "System of equations",
    },
    "type.calculus_limit": {
        "km": "លីមីតនៃអនុគមន៍",
        "en": "Calculus limit",
    },
    "type.calculus_derivative": {
        "km": "ដេរីវេនៃអនុគមន៍",
        "en": "Calculus derivative",
    },
    "type.calculus_integral": {
        "km": "អាំងតេក្រាល",
        "en": "Calculus integral",
    },
    "type.calculus_differential_equation": {
        "km": "សមីការឌីផេរ៉ង់ស្យែល",
        "en": "Differential equation",
    },
    "type.expression_simplification": {
        "km": "ការសម្រួលកន្សោម",
        "en": "Expression simplification",
    },
    "type.expression_factorization": {
        "km": "ការដាក់ជាផលគុណកត្តា",
        "en": "Factorization",
    },
    "type.polynomial_factorization": {
        "km": "ការដាក់ពហុធាជាផលគុណកត្តា",
        "en": "Polynomial factorization",
    },
    "type.expression_expansion": {
        "km": "ការពន្លាតកន្សោម",
        "en": "Expression expansion",
    },
    "type.polynomial_expansion": {
        "km": "ការពន្លាតពហុធា",
        "en": "Polynomial expansion",
    },
    "type.sequence": {
        "km": "ស្វ៊ីតចំនួន",
        "en": "Number sequence",
    },
    "type.sequence_limit": {
        "km": "លីមីតនៃស្វ៊ីត",
        "en": "Sequence limit",
    },
    "type.sequence_convergence": {
        "km": "ភាពរួមនៃស្វ៊ីត",
        "en": "Sequence convergence",
    },
    "type.sequence_recurrence": {
        "km": "ស្វ៊ីតកំណត់ដោយទំនាក់ទំនងកំណើន",
        "en": "Recurrence relation sequence",
    },
    "type.arithmetic_expression": {
        "km": "កន្សោមលេខនព្វន្ធ",
        "en": "Arithmetic expression",
    },
    "type.algebraic_expression": {
        "km": "កន្សោមពិជគណិត",
        "en": "Algebraic expression",
    },

    # Mathematical Operations & Transformations
    "op.add": {
        "km": "បូក",
        "en": "Add",
    },
    "op.subtract": {
        "km": "ដក",
        "en": "Subtract",
    },
    "op.multiply": {
        "km": "គុណ",
        "en": "Multiply",
    },
    "op.divide": {
        "km": "ចែក",
        "en": "Divide",
    },
    "op.factor": {
        "km": "ដាក់ជាផលគុណកត្តា",
        "en": "Factor",
    },
    "op.expand": {
        "km": "ពន្លាត",
        "en": "Expand",
    },
    "op.substitute": {
        "km": "ជំនួស",
        "en": "Substitute",
    },
    "op.simplify": {
        "km": "សម្រួល",
        "en": "Simplify",
    },
    "op.isolate_variable": {
        "km": "ទាញរកអថេរ",
        "en": "Isolate variable",
    },
    "op.move_term": {
        "km": "ផ្ទេរតួ",
        "en": "Move term",
    },
    "op.combine_like_terms": {
        "km": "បូកដកតួដូចគ្នា",
        "en": "Combine like terms",
    },
    "op.apply_quadratic_formula": {
        "km": "អនុវត្តរូបមន្តឌីសគ្រីមីណង់ (Δ)",
        "en": "Apply quadratic formula (Δ)",
    },
    "op.differentiate": {
        "km": "រកដេរីវេ",
        "en": "Differentiate",
    },
    "op.integrate": {
        "km": "គណនាអាំងតេក្រាល",
        "en": "Integrate",
    },
    "op.verify": {
        "km": "ផ្ទៀងផ្ទាត់",
        "en": "Verify",
    },

    # Pedagogical Step Labels & Structure
    "step.order": {
        "km": "ជំហានទី {order}",
        "en": "Step {order}",
    },
    "step.initial_equation": {
        "km": "សមីការដើម",
        "en": "Initial equation",
    },
    "step.initial_expression": {
        "km": "កន្សោមដើម",
        "en": "Initial expression",
    },
    "step.final_answer": {
        "km": "ចម្លើយចុងក្រោយ",
        "en": "Final answer",
    },
    "step.verification": {
        "km": "ការផ្ទៀងផ្ទាត់ចម្លើយ",
        "en": "Solution verification",
    },
    "pedagogy.what": {
        "km": "សកម្មភាព (What)",
        "en": "Action (What)",
    },
    "pedagogy.why": {
        "km": "មូលហេតុ (Why)",
        "en": "Rationale (Why)",
    },
    "pedagogy.rule": {
        "km": "រូបមន្តអនុវត្ត",
        "en": "Rule / Formula applied",
    },

    # Logical Connectives in Proofs & Solutions
    "connective.therefore": {
        "km": "ដូច្នេះ",
        "en": "Therefore",
    },
    "connective.because": {
        "km": "ពីព្រោះ",
        "en": "Because",
    },
    "connective.since": {
        "km": "ដោយសារ",
        "en": "Since",
    },
    "connective.we_have": {
        "km": "យើងបាន",
        "en": "We have",
    },
    "connective.we_obtain": {
        "km": "យើងទទួលបាន",
        "en": "We obtain",
    },
    "connective.given_that": {
        "km": "ដោយដឹងថា",
        "en": "Given that",
    },
    "connective.substituting": {
        "km": "ជំនួស",
        "en": "Substituting",
    },
    "connective.hence": {
        "km": "ហេតុនេះ",
        "en": "Hence",
    },
    "connective.implies": {
        "km": "នាំឱ្យ",
        "en": "Implies",
    },
    "connective.equivalent_to": {
        "km": "សមមូលនឹង",
        "en": "Equivalent to",
    },
}


def translate(
    key: str,
    lang: str | Language | None = None,
    default: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Translate a key into the target language with variable interpolation.

    Args:
        key: Dot-separated key or category string (e.g. "type.linear_equation", "status.success")
        lang: Target language ("km", "en", Language.KM, Language.EN), or current active language if None
        default: Fallback string if key is not found
        **kwargs: Variables to interpolate into the template (e.g. order=1, error="...")

    Returns:
        Translated string, formatted with variables if provided.

    Examples:
        >>> translate("status.success", "km")
        'ជោគជ័យ'
        >>> translate("status.success", "en")
        'Success'
        >>> translate("step.order", "km", order=2)
        'ជំហានទី 2'
    """
    active_lang = get_current_language() if lang is None else lang
    target_lang = normalize_language(active_lang)
    entry = TRANSLATIONS.get(key)

    if entry is not None:
        text = entry.get(target_lang.value)
        if text is None:
            # Fall back to English, then to any available language
            text = entry.get(FALLBACK_LANGUAGE.value) or next(iter(entry.values()), None)
    else:
        text = default

    if text is None:
        # Ultimate fallback: return key or default
        text = default if default is not None else key

    if kwargs and "{" in text:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text

    return text


# Short alias
t = translate


def get_bilingual(key: str, **kwargs: Any) -> dict[str, str]:
    """
    Retrieve both Khmer and English translations for a key.

    Returns:
        Dict with "km" and "en" keys: {"km": "...", "en": "..."}
    """
    km_text = translate(key, Language.KM, **kwargs)
    en_text = translate(key, Language.EN, **kwargs)
    return {"km": km_text, "en": en_text}


def format_bilingual(key: str, separator: str = " / ", **kwargs: Any) -> str:
    """
    Format a translation key as a bilingual string: 'Khmer / English'.

    Example:
        >>> format_bilingual("status.success")
        'ជោគជ័យ / Success'
    """
    bi = get_bilingual(key, **kwargs)
    return f"{bi['km']}{separator}{bi['en']}"


def register_translation(key: str, km: str, en: str) -> None:
    """Dynamically register or override a translation key."""
    TRANSLATIONS[key] = {
        Language.KM.value: km,
        Language.EN.value: en,
    }


def get_all_translations(lang: str | Language | None = None) -> dict[str, Any]:
    """
    Return all translations dictionary.
    If lang is specified, returns {key: translated_text}.
    If lang is None, returns full {key: {"km": ..., "en": ...}} dictionary.
    """
    if lang is None:
        return dict(TRANSLATIONS)

    target_lang = normalize_language(lang).value
    return {
        key: entry.get(target_lang, entry.get(FALLBACK_LANGUAGE.value, key))
        for key, entry in TRANSLATIONS.items()
    }
