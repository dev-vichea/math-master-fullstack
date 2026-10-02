"""
Intent classification for Khmer and English math requests.

`IntentClassifier` is an abstract interface: ships a rule-based implementation
(fast, deterministic, zero dependencies) supporting natural phrasing in both
Khmer and English.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum


class MathIntent(str, Enum):
    SOLVE_EQUATION = "solve_equation"
    EVALUATE_EXPRESSION = "evaluate_expression"
    SIMPLIFY_EXPRESSION = "simplify_expression"
    UNKNOWN = "unknown"


class IntentClassifier(ABC):
    @abstractmethod
    def classify(self, normalized_text: str) -> MathIntent: ...


# Khmer phrasings for "solve for x" / "find the value of x"
_SOLVE_KEYWORDS_KM = [
    "ដោះស្រាយ",  # solve
    "ជួយខ្ញុំដោះស្រាយ",  # help me solve
    "ជួយដោះស្រាយ",  # help solve
    "រកតម្លៃ",  # find the value
    "រក x",
    "រក",  # find
    "ស្វែងរក",  # search/find
    "តម្លៃប៉ុន្មាន",  # what is the value / how much
    "តម្លៃ",  # value
    "ណា",  # what (in questions)
    "គណនា",  # calculate/compute
    "គិត",  # calculate
    "ស្វែងយក",  # seek/find
    "ដោះ",  # solve (short form)
]

# English phrasings for "solve"
_SOLVE_KEYWORDS_EN = [
    "solve",
    "solve for",
    "find the value",
    "find the root",
    "find roots",
    "find x",
    "find y",
    "find z",
    "determine",
]

_SIMPLIFY_KEYWORDS_KM = [
    "ធ្វើឲ្យសាមញ្ញ",  # simplify
    "កាត់បន្ថយ",  # reduce
    "សាមញ្ញ",  # simple
    "បង្រួម",  # condense/reduce
    "កាត់",  # cut/reduce
]

_SIMPLIFY_KEYWORDS_EN = [
    "simplify",
    "reduce",
    "factorize",
    "factor",
    "expand",
    "condense",
]

_EVALUATE_KEYWORDS_KM = [
    "គណនា",  # calculate
    "គិត",  # think/calculate
    "ផ្ដល់ជូន",  # provide/give
    "លទ្ធផល",  # result
    "ចម្លើយ",  # answer
]

_EVALUATE_KEYWORDS_EN = [
    "evaluate",
    "calculate",
    "compute",
    "what is",
    "result",
    "answer",
    "sum of",
    "product of",
]

_FRACTION_KEYWORDS = [
    "ប្រភាគ",  # fraction
    "ប្រភាគទសភាគ",  # decimal fraction
    "ប្រភាគធម្មតា",  # common fraction
    "fraction",
    "fractions",
]

_PERCENTAGE_KEYWORDS = [
    "ភាគរយ",  # percentage
    "%",
    "ភាគ",  # percent (short)
    "ចំនួនភាគរយ",  # percentage amount
    "percent",
    "percentage",
]

_WORD_PROBLEM_KEYWORDS_KM = [
    "បញ្ហា",  # problem
    "សំណួរ",  # question
    "លំហាត់",  # exercise
    "តើ",  # question marker
]

_WORD_PROBLEM_KEYWORDS_EN = [
    "problem",
    "question",
    "exercise",
    "given that",
    "if",
    "when",
    "how much",
]


def _contains_word(text_lower: str, keywords: list[str]) -> bool:
    """Check if any keyword is present in text with word boundaries for Latin words."""
    for kw in keywords:
        if re.search(r"[a-zA-Z]", kw):
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_lower):
                return True
        else:
            if kw in text_lower:
                return True
    return False


class RuleBasedIntentClassifier(IntentClassifier):
    def classify(self, normalized_text: str) -> MathIntent:
        text_lower = normalized_text.lower()

        # Priority 0: Fraction or percentage keywords override general keywords
        has_fraction = _contains_word(text_lower, _FRACTION_KEYWORDS)
        has_percentage = _contains_word(text_lower, _PERCENTAGE_KEYWORDS)
        if has_fraction or has_percentage:
            return MathIntent.EVALUATE_EXPRESSION

        # Priority 1: Explicit simplify keywords (Khmer and English)
        if _contains_word(text_lower, _SIMPLIFY_KEYWORDS_KM + _SIMPLIFY_KEYWORDS_EN):
            return MathIntent.SIMPLIFY_EXPRESSION

        # Priority 2: Equations (contains equals sign or inequality)
        if "=" in normalized_text or any(
            op in normalized_text for op in ["<=", ">=", "<", ">", "≤", "≥"]
        ):
            return MathIntent.SOLVE_EQUATION

        # Priority 3: Explicit solve keywords (Khmer and English)
        if _contains_word(text_lower, _SOLVE_KEYWORDS_KM + _SOLVE_KEYWORDS_EN):
            return MathIntent.SOLVE_EQUATION

        # Priority 4: Evaluate keywords suggest computation
        if _contains_word(text_lower, _EVALUATE_KEYWORDS_KM + _EVALUATE_KEYWORDS_EN):
            return MathIntent.EVALUATE_EXPRESSION

        # Priority 5: Word problem markers with numbers suggest evaluation
        has_word_problem = _contains_word(
            text_lower, _WORD_PROBLEM_KEYWORDS_KM + _WORD_PROBLEM_KEYWORDS_EN
        )
        has_numbers = bool(re.search(r"\d", normalized_text))
        if has_word_problem and has_numbers:
            return MathIntent.EVALUATE_EXPRESSION

        # Priority 6: Any expression with numbers or mathematical operators with variables
        has_math_ops = bool(re.search(r"[+\-*/^()]", normalized_text))
        if has_numbers or (has_math_ops and bool(re.search(r"[a-zA-Z]", normalized_text))):
            return MathIntent.EVALUATE_EXPRESSION

        return MathIntent.UNKNOWN
