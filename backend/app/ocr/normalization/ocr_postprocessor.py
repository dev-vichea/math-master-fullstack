"""
OCR post-processing and math text sanitization.

Cleans and normalizes raw text from OCR engines (Tesseract, Kiri OCR, etc.),
repairing common optical character recognition artifacts, math notation errors,
superscript/exponent formatting, and multilingual whitespace issues.
"""

from __future__ import annotations

import re
import unicodedata

from app.core.khmer.digits import khmer_digits_to_arabic

# Unicode superscripts to standard caret notation mapping
_SUPERSCRIPT_MAP = {
    "⁰": "^0",
    "¹": "^1",
    "²": "^2",
    "³": "^3",
    "⁴": "^4",
    "⁵": "^5",
    "⁶": "^6",
    "⁷": "^7",
    "⁸": "^8",
    "⁹": "^9",
    "⁺": "^+",
    "⁻": "^-",
}

# Math dash/minus variations to ASCII hyphen
_MINUS_VARIANTS = ["−", "–", "—", "ｰ", "‐"]

# Math multiplication variations to asterisk
_MULT_VARIANTS = ["×", "✕", "✖", "·", "∙"]

# Inequality normalization
_INEQUALITY_MAP = {
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "≼": "<=",
    "≽": ">=",
}


def sanitize_ocr_math_text(raw_text: str) -> str:
    """
    Standardize OCR text into canonical mathematical and multilingual format.

    Steps:
    1. Unicode normalization (NFC)
    2. Khmer digits to Arabic digits (០-៩ -> 0-9)
    3. Unicode superscripts to caret notation (x² -> x^2)
    4. Operator standardization (minus − -> -, times × -> *, divide ÷ -> /)
    5. OCR collapsed exponent detection (x2 -> x^2 in algebraic context)
    6. Fix OCR fragmented numbers and variable gaps (1 5 -> 15, 2 x -> 2x)
    7. OCR character confusion repairs (O/0, l/1 in digit contexts)
    """
    if not raw_text:
        return ""

    text = unicodedata.normalize("NFC", raw_text)

    # 1. Convert Khmer digits to Arabic
    text = khmer_digits_to_arabic(text)

    # 2. Normalize Khmer punctuation chan '៖'
    text = text.replace("៖", ":")

    # 3. Unicode superscripts (x² -> x^2, x³ -> x^3)
    for sup_char, caret_expr in _SUPERSCRIPT_MAP.items():
        text = text.replace(sup_char, caret_expr)
    # Collapse double carets from sign + exponent (e.g. ^-^1 -> ^-1)
    text = re.sub(r"\^([+\-])\^", r"^\1", text)

    # 4. Standardize minus signs
    for dash in _MINUS_VARIANTS:
        text = text.replace(dash, "-")

    # 5. Standardize multiplication signs
    for mult in _MULT_VARIANTS:
        text = text.replace(mult, "*")

    # 6. Standardize division signs
    text = text.replace("÷", "/")

    # 7. Standardize inequality signs
    for ineq_char, ascii_ineq in _INEQUALITY_MAP.items():
        text = text.replace(ineq_char, ascii_ineq)

    # 8. Colon as division between pure numbers (e.g., '12 : 3' -> '12 / 3', not '1 : 2x')
    text = re.sub(r"(?<=\d)\s*:\s*(?=\d+\b(?![a-zA-Z]))", " / ", text)

    # 9. Detect OCR collapsed exponents (e.g. 'x2 - 25x + 15 = 0', '10x2 + 8x = 32', 'x2 = 16')
    # Where a single variable letter is immediately followed by digit 2-9 and then an operator/space/end
    text = re.sub(
        r"(?<=[a-zA-Z])([2-9])(?=[+\-*/=<>≤≥\s\),]|;|$)",
        r"^\1",
        text,
    )

    # 10. Fix OCR digit confusion (e.g., uppercase O in numbers like '2O' or '1OO')
    # Guard against corrupting words or LaTeX commands (e.g., '\to0' must remain '\to0')
    while re.search(r"(?<=\d)[Oo]", text):
        text = re.sub(r"(?<=\d)[Oo]", "0", text)
    while re.search(r"(?<![a-zA-Z\\])[Oo](?=\d)", text):
        text = re.sub(r"(?<![a-zA-Z\\])[Oo](?=\d)", "0", text)

    # 11. Fix OCR 'l' or 'I' confused with digit 1 in numeric tokens (e.g., 'l5', 'l00')
    text = re.sub(r"(?<=[+\-*/=<>≤≥\s\(])[lI](?=\d)", "1", text)
    text = re.sub(r"(?<=\d)[lI](?=[+\-*/=<>≤≥\s\)]|$)", "1", text)

    # 12. Fix fragmented numbers from OCR spacing (e.g., '1 5' surrounded by operators or boundaries)
    # Be careful not to merge numbers across commas or list separators
    text = re.sub(r"(?<=\b\d)\s+(?=\d\b)", "", text)

    # 13. Fix horizontal spaces between numeric coefficients and variable: '2 x' -> '2x'
    text = re.sub(r"(?<=\d)[ \t]+([a-zA-Z])(?![a-zA-Z\)\.\:៖])", r"\1", text)

    # 14. Fix Pix2Tex / LaTeX-OCR misrecognitions:
    # 14a. Fix \Im with arrow subscript to \lim (e.g., \Im_{n\to\infty} -> \lim_{n\to\infty})
    text = re.sub(r"\\Im(?=\s*[_\{])", r"\\lim", text)

    # 14b. Fix stray \cdot before variable in limit subscript (e.g., \lim_{\cdot n \to ...} -> \lim_{n \to ...})
    text = re.sub(r"\\cdot\s*([a-zA-Z])\s*\\to", r"\1 \\to", text)

    # 14c. Unwrap LaTeX font commands (\mathbf, \mathrm, \mathit, \text) to prevent parser truncation
    text = re.sub(r"\\(?:mathbf|mathrm|mathit|text)\{([^{}]+)\}", r"\1", text)

    # 14d. Fix repeated trig argument artifacts from glyph kerning (e.g. \sin n n -> \sin(n))
    text = re.sub(r"\\(sin|cos|tan)\s*([a-zA-Z])\s*\{?\2\}?", r"\\\1(\2)", text)

    # 14e. Fix digit 5 confused with 's' or '{s}' before variable with exponent (e.g., '{s} n^2' or 'sn^2' -> '5n^2')
    text = re.sub(r"(?:\{\s*[sS]\s*\}|\b[sS]\b)\s*(\{?[a-zA-Z]\}?\^)", r"5\1", text)
    text = re.sub(r"(?<=[+\-*/=\(\{\s/])\s*[sS](?=[a-zA-Z]\^)", "5", text)

    # 14f. Fix \cos{\pi}n, \cos\pi n without argument parentheses -> \cos(\pi n)
    text = re.sub(r"\\(sin|cos|tan)(?:\{\\pi\}|\s*\\pi)\s*([a-zA-Z])", r"\\\1(\\pi \2)", text)

    # 15. Clean multiple spaces
    text = re.sub(r"[ \t]+", " ", text).strip()

    return text
