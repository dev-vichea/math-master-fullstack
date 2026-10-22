r"""
Mathematical Condition and Domain Extractor.

Extracts domain intervals, constraints, and initial conditions from bilingual
(Khmer + English + LaTeX) mathematical text or OCR output:
- Domain intervals: "កំណត់លើ (-1, 1)", "លើចន្លោះ [0, \pi]", "x \in (-1, 1)"
- Constraints: "ចំពោះ x > 0", "where x != 0", "for x >= 1"
- Initial conditions: "y(0) = -2", "y'(0) = 3", "y(\ln 4) = 1/5"

Ensures the primary formula sent to MathLive is pure, clean math without
dangling prose or condition noise.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class ExtractedCondition(NamedTuple):
    raw_condition: str
    condition_type: str  # "domain_interval", "initial_condition", "constraint", "other"
    normalized_condition: str
    interval: str | None = None


# Khmer and English domain interval keywords
_DOMAIN_KEYWORDS_KM = [
    "កំណត់លើ",
    "កំណត់លេ",
    "កំនត់លើ",
    "លើចន្លោះ",
    "លើ",
]

_CONSTRAINT_KEYWORDS_KM = [
    "ចំពោះ",
    "ដែល",
    "កាលណា",
    "បើ",
    "បើសិន",
]


def extract_condition_and_math(text: str) -> tuple[str, ExtractedCondition | None]:
    """
    Separates a mathematical expression from any trailing domain condition or constraint.

    Args:
        text: Raw or postprocessed formula text (e.g. "y' = \\frac{x}{x^2-1} កំណត់លើ (-1, 1)")

    Returns:
        tuple of (clean_formula, extracted_condition_or_none)
    """
    if not text:
        return "", None

    # Pre-normalize dashes and hyphens commonly emitted by OCR
    s = text.strip()
    s = re.sub(r"[—–−‐]", "-", s)
    s = re.sub(r"-\s*(\d+)", r"-\1", s)

    # 1. Check for Khmer domain interval: e.g. "កំណត់លើ (-1, 1)" or "កំណត់លើ ]-1, 1["
    m_domain_km = re.search(
        r"([,;]?\s*(?:កំណត់លើ|កំណត់លេ|កំនត់លើ|លើចន្លោះ|លើ)\s*(?:ចន្លោះ\s*)?"
        r"(?:\\left)?\s*([(\[\]])\s*([-+]?\d*(?:\.\d+)?|[a-zA-Z\\]+)\s*[,;\s\\]+\s*([-+]?\d*(?:\.\d+)?|[a-zA-Z\\]+)\s*(?:\\right)?\s*([)\[\]]))",
        s,
    )
    if m_domain_km:
        raw_full = m_domain_km.group(1).strip().lstrip(",;")
        left_bracket = m_domain_km.group(2)
        start_val = m_domain_km.group(3)
        end_val = m_domain_km.group(4)
        right_bracket = m_domain_km.group(5)

        interval_str = f"{left_bracket}{start_val}, {end_val}{right_bracket}"
        clean_math = s[:m_domain_km.start()].strip().rstrip(",; ")

        return clean_math, ExtractedCondition(
            raw_condition=raw_full,
            condition_type="domain_interval",
            normalized_condition=f"កំណត់លើ {interval_str}",
            interval=interval_str,
        )

    # 2. Check for LaTeX interval syntax: e.g. ", x \in (-1, 1)" or "(-1, 1)" at end of formula
    m_interval_tail = re.search(
        r"([,;]?\s*(?:x\s*\\in\s*)?(?:\\left)?\s*([(\[])\s*([-+]?\d*(?:\.\d+)?)\s*[,;\s\\]+\s*([-+]?\d*(?:\.\d+)?)\s*(?:\\right)?\s*([)\]]))\s*$",
        s,
    )
    if m_interval_tail:
        prefix = s[:m_interval_tail.start()].strip()
        if "=" in prefix or r"\int" in prefix or "y'" in prefix:
            raw_full = m_interval_tail.group(1).strip().lstrip(",;")
            left_b = m_interval_tail.group(2)
            val1 = m_interval_tail.group(3)
            val2 = m_interval_tail.group(4)
            right_b = m_interval_tail.group(5)
            interval_str = f"{left_b}{val1}, {val2}{right_b}"

            clean_math = prefix.rstrip(",; ")
            return clean_math, ExtractedCondition(
                raw_condition=raw_full,
                condition_type="domain_interval",
                normalized_condition=f"x \\in {interval_str}",
                interval=interval_str,
            )

    # 3. Check for Khmer or English constraint: e.g. "ចំពោះ x > 0" or "where x != 0"
    m_constraint = re.search(
        r"([,;]?\s*(?:ចំពោះ|ដែល|កាលណា|where|for)\s+([a-zA-Z]\s*(?:!=|≠|<=|>=|<|>|=)\s*[-+]?\d+))\s*$",
        s,
    )
    if m_constraint:
        raw_full = m_constraint.group(1).strip().lstrip(",;")
        cond_expr = m_constraint.group(2).strip()
        clean_math = s[:m_constraint.start()].strip().rstrip(",; ")
        return clean_math, ExtractedCondition(
            raw_condition=raw_full,
            condition_type="constraint",
            normalized_condition=cond_expr,
        )

    # 4. Check for parenthesized constraints: e.g. "(a \neq 0, b \neq 0, a \neq b)" or "(x != 0)"
    m_paren = re.search(
        r"([,;]?\s*\(\s*([a-zA-Z\\]+\s*(?:!=|≠|<=|>=|<|>|=|\\neq)\s*[^)]+)\))\s*$",
        s,
    )
    if m_paren:
        raw_full = m_paren.group(1).strip().lstrip(",;")
        cond_expr = m_paren.group(2).strip()
        clean_math = s[:m_paren.start()].strip().rstrip(",; ")
        return clean_math, ExtractedCondition(
            raw_condition=raw_full,
            condition_type="constraint",
            normalized_condition=cond_expr,
        )

    return s, None
