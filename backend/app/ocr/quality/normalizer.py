r"""
Deterministic Math Normalizer.

Performs safe, structural transformations only:
- Whitespace normalization
- LaTeX command syntax standardization
- Unicode operator to LaTeX/ASCII mapping
- Safe function prefixing (sin -> \sin)
- Detection and isolation of non-math prefixes (e.g., exercise numbering '1964,', '25.', '(a)')
- Detection and stripping of trailing OCR noise/punctuation

No semantic guessing (e.g. never mutates digits or variable names).
"""

from __future__ import annotations

import re
import unicodedata

# Unicode to ASCII/LaTeX operator mappings
_UNICODE_OPERATORS = {
    "−": "-",
    "–": "-",
    "—": "-",
    "×": "*",
    "✕": "*",
    "✖": "*",
    "·": "*",
    "∙": "*",
    "÷": "/",
    "∕": "/",
    "≠": "!=",
    "≤": r"\le ",
    "≥": r"\ge ",
    "⩽": r"\le ",
    "⩾": r"\ge ",
    "∞": r"\infty ",
    "→": r"\to ",
    "⇒": r"\implies ",
    "∫": r"\int ",
    "∬": r"\iint ",
    "∭": r"\iiint ",
    "π": r"\pi ",
}

# Common mathematical functions that should have a backslash in LaTeX
_MATH_FUNCS = ["sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan", "ln", "log", "exp", "lim"]

# Pattern for leading non-math prefixes like '1964,', '25.', '(a)', 'ឃ.', 'Ex 3:', 'No. 5'
_PREFIX_PATTERN = re.compile(
    r"^\s*("
    r"(?:(?:exercise|ex|problem|no|№)\s*[\.\#:]?\s*\d+[\.\,:]?)"          # Exercise 1., No. 5:
    r"|(?:\d{1,4}\s*[\.\,:]\s*(?!\d))"                                    # 1964, or 25. (not followed by digit so 3.14 isn't matched)
    r"|(?:\(\s*(?:[a-zA-Z]|\d{1,3}|[\u1780-\u17a2]|[\u17e0-\u17e9]{1,3})\s*\)\s*[\.\,:]?)"  # (a) or (1) or (ឃ)
    r"|(?:[a-zA-Z\u1780-\u17a2]{1,2}\s*[\.\,:]\s*)"                      # a. or ឃ.
    r"|(?:[\u17e0-\u17e9]{1,4}\s*[\.\,:]\s*)"                            # ២៥.
    r"|(?:\\[a-zA-Z]+\{[a-zA-Z0-9\u1780-\u17a2]+\}\s*[\.\,:]\s*)"        # \mathbf{2}.
    r")\s*",
    re.IGNORECASE,
)

# Pattern for trailing non-math noise (e.g. '~v', 'ฯ', trailing punctuation)
_SUFFIX_PATTERN = re.compile(
    r"(?:[\s,;:.|ฯ\\]+|~\s*[a-zA-Z]?|\\[a-zA-Z]+)+$"
)


def safe_normalize_math(raw_text: str) -> tuple[str, list[str], str | None, str | None]:
    """
    Safely normalizes raw OCR text into standardized LaTeX/math representation.

    Returns:
        tuple of (normalized_math, warnings, detected_prefix, detected_suffix)
    """
    if not raw_text or not raw_text.strip():
        return "", ["Empty text"], None, None

    warnings: list[str] = []
    text = raw_text.strip()

    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Extract and isolate non-math prefix
    detected_prefix: str | None = None
    m_prefix = _PREFIX_PATTERN.match(text)
    if m_prefix:
        prefix_candidate = m_prefix.group(1).strip()
        remainder = text[m_prefix.end():].strip()
        # Only detach prefix if remainder looks like math
        if remainder and (
            any(c in remainder for c in "=+-*/\\^_{}()[]")
            or any(fn in remainder.lower() for fn in _MATH_FUNCS)
            or re.search(r"[a-zA-Z]\b", remainder)
        ):
            detected_prefix = prefix_candidate
            text = remainder
            warnings.append(f"Detached non-math prefix '{detected_prefix}'")

    # 3. Extract and isolate trailing noise/suffix
    detected_suffix: str | None = None
    m_suffix = _SUFFIX_PATTERN.search(text)
    if m_suffix and len(m_suffix.group(0).strip()) > 0:
        detected_suffix = m_suffix.group(0).strip()
        text = text[:m_suffix.start()].strip()
        warnings.append(f"Trimmed trailing noise '{detected_suffix}'")

    # 4. Standardize Unicode mathematical operators
    for uni_char, replacement in _UNICODE_OPERATORS.items():
        if uni_char in text:
            text = text.replace(uni_char, replacement)

    # 5. Clean LaTeX spacing tokens (\;, \quad, \qquad, \!)
    text = re.sub(r"\\[;,!:]", " ", text)
    text = re.sub(r"\\(?:quad|qquad|hfill|vfill|thickspace|medspace|thinspace)\b", " ", text)

    # Ensure whitespace between digits and LaTeX commands (e.g. 3\frac -> 3 \frac)
    text = re.sub(r"(\d+)\s*(\\[a-zA-Z]+)", r"\1 \2", text)

    # 6. Normalize common LaTeX function constructs
    text = text.replace(r"\operatorname*{lim}", r"\lim").replace(r"\operatorname{lim}", r"\lim")
    text = text.replace(r"\to\infty", r"\to \infty")

    # Ensure backslash for known math functions when missing
    for func in _MATH_FUNCS:
        # Match func not preceded by backslash or letter, and followed by non-letter
        pattern = re.compile(rf"(?<![\\a-zA-Z]){func}(?![a-zA-Z])")
        text = pattern.sub(rf"\\{func}", text)

    # 7. Clean double backslash escapes introduced by serialization (e.g. \\lim -> \lim)
    text = (
        text.replace(r"\\lim", r"\lim")
        .replace(r"\\frac", r"\frac")
        .replace(r"\\sqrt", r"\sqrt")
        .replace(r"\\sin", r"\sin")
        .replace(r"\\cos", r"\cos")
        .replace(r"\\tan", r"\tan")
        .replace(r"\\ln", r"\ln")
        .replace(r"\\pi", r"\pi")
        .replace(r"\\to", r"\to")
        .replace(r"\\infty", r"\infty")
    )

    # 8. Standardize limit subscript braces: \lim_ {x \to c} -> \lim_{x \to c}
    text = re.sub(r"\\lim\s*_\s*\{", r"\\lim_{", text)
    text = re.sub(r"\\frac\s*\{", r"\\frac{", text)
    text = re.sub(r"\\sqrt\s*\{", r"\\sqrt{", text)

    # 9. Normalize fraction brace syntax (e.g. \frac{a}b -> \frac{a}{b})
    text = re.sub(r"\\frac\s*\{([^}]+)\}\s*([a-zA-Z0-9])\b", r"\\frac{\1}{\2}", text)

    # 10. Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text, warnings, detected_prefix, detected_suffix
