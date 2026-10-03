"""
Pull the mathematical expression out of a sentence that mixes Khmer or English
words and math, e.g.:
- "ដោះស្រាយសមីការនេះ 2x + 5 = 15" -> "2x+5=15"
- "Exercise 1: Solve for x: 3x - 9 = 0" -> "3x-9=0"
- "Exercise (លំហាត់): Find the value of x if 4x + 10 = 30" -> "4x+10=30"

Uses the intelligent bilingual exercise parser with backward-compatible fallback.
"""

from __future__ import annotations

import re

# A run of characters that looks like math: digits, letters (variables),
# operators, parentheses, decimal points, '=', inequality signs, whitespace,
# and LaTeX syntax (backslashes, braces, underscores).
_EXPRESSION_RUN = re.compile(r"[0-9a-zA-Z.\+\-\*/\^=()\[\]\s<>=≤≥\\{}_'’|,]{3,}")

# Two-or-more consecutive Latin letters that are NOT part of a LaTeX command
_MULTI_LETTER_WORD = re.compile(r"(?<!\\)\b[a-zA-Z]{2,}\b")


def extract_expression(normalized_text: str) -> str | None:
    """Return the best-guess math substring from Khmer or English text,
    or None if nothing looking like math was found."""
    if not normalized_text:
        return None

    # Use the smart bilingual exercise parser
    try:
        from app.parser.exercise_parser.exercise_parser import parse_exercise

        parsed = parse_exercise(normalized_text)
        if parsed.primary_expression:
            return parsed.primary_expression
    except Exception:
        pass

    # Fallback to standard regex heuristic
    from app.parser.exercise_parser.exercise_parser import _strip_non_math_words

    text_without_words = _strip_non_math_words(normalized_text)

    candidates = _EXPRESSION_RUN.findall(text_without_words)
    if not candidates:
        return None

    # Check if verification sentence with multiple equations
    if any(k in normalized_text for k in ("ជាចម្លើយនៃសមីការ", "ជាចម្លើយ", "is a solution to", "is a solution of", "solution of the differential equation")):
        eq_runs = [c.strip() for c in candidates if "=" in c and len(c.strip()) >= 3]
        if len(eq_runs) >= 2:
            return f"{eq_runs[0]} , {eq_runs[1]}"

    # Prefer candidates that contain at least one digit
    with_digits = [c for c in candidates if re.search(r"\d", c)]
    pool = with_digits or candidates

    best = max(pool, key=len).strip()
    if "\\" in best or "{" in best:
        best = re.sub(r"\s+", " ", best).strip()
    else:
        best = re.sub(r"\s+", "", best)

    best = best.strip(".:;=, ")
    while best.endswith("\\"):
        best = best[:-1].rstrip(".:;=, ")
    return best or None
