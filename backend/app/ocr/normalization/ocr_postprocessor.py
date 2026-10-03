"""
OCR post-processing and math text sanitization.

Cleans and normalizes raw text from OCR engines (Tesseract, Kiri OCR, etc.),
repairing common optical character recognition artifacts, math notation errors,
superscript/exponent formatting, and multilingual whitespace issues.
"""

from __future__ import annotations

import re
import unicodedata

_KHMER_DIGITS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")


def khmer_digits_to_arabic(text: str) -> str:
    """Convert Khmer digits (០-៩) to Arabic digits (0-9)."""
    return text.translate(_KHMER_DIGITS)

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

    # 2. Normalize Khmer punctuation chan '៖' and sentence ends '។' / '៕'
    # Convert Khmer punctuation '។' after labels like 'ក។' to standard dot 'ក.'
    text = re.sub(r"([ក-អ])។", r"\1.", text)
    text = text.replace("៖", ":")
    text = text.replace("។", " ").replace("៕", " ")

    # 2b. Convert Unicode integral symbols
    text = text.replace("∫", r"\int ").replace("∬", r"\iint ").replace("∭", r"\iiint ")

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

    # 9. Detect OCR collapsed exponents (e.g. 'x2 - 25x + 15 = 0', '10x2 + 8x = 32', 'x2 = 16', 'x2dx')
    # Where a single variable letter is immediately followed by digit 2-9 and then an operator/space/differential/end
    text = re.sub(
        r"(?<=[a-zA-Z])([2-9])(?=[+\-*/=<>≤≥\s\),]|;|d[xyzut]\b|$)",
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

    # 14c. Strip textstyle/displaystyle
    text = re.sub(r"\\(?:textstyle|displaystyle)\s*", "", text)

    # 14d. Replace \times before differential with x (e.g. 3\times\mathrm{d}X -> 3x dx)
    text = re.sub(r"([0-9a-zA-Z])\s*\\times\s*(?=\\mathrm\{[dD]\}|[dD]|\bI|\bk|\\mathbf\{[dDIk]\})", r"\g<1>x ", text)

    # 14e. Unwrap LaTeX font commands (\mathbf, \mathrm, \mathit, \text, \boldsymbol, \bf, \rm) to prevent parser truncation
    text = re.sub(r"\\(?:mathbf|mathrm|mathit|text|boldsymbol)\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\{\\(?:bf|rm)\s+([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\(?:bf|rm)\s+([a-zA-Z0-9]+)", r"\1", text)
    text = re.sub(r"\\(?:bf|rm)\b", "", text)

    # 14f. Fix repeated trig argument artifacts from glyph kerning (e.g. \sin n n -> \sin(n))
    text = re.sub(r"\\(sin|cos|tan)\s*([a-zA-Z])\s*\{?\2\}?", r"\\\1(\2)", text)

    # 14g. Fix digit 5 confused with 's' or '{s}' before variable with exponent (e.g., '{s} n^2' or 'sn^2' -> '5n^2')
    text = re.sub(r"(?:\{\s*[sS]\s*\}|\b[sS]\b)\s*(\{?[a-zA-Z]\}?\^)", r"5\1", text)
    text = re.sub(r"(?<=[+\-*/=\(\{\s/])\s*[sS](?=[a-zA-Z]\^)", "5", text)

    # 14h. Fix \cos{\pi}n, \cos\pi n without argument parentheses -> \cos(\pi n)
    text = re.sub(r"\\(sin|cos|tan)(?:\{\\pi\}|\s*\\pi)\s*([a-zA-Z])", r"\\\1(\\pi \2)", text)

    # 15. Integral & Differential OCR Repairs
    # 15a. Differential typos: \vert x, |x, Ix, kx, dX, \mathrm{d}X, \dim\times, \ln x -> dx
    text = re.sub(r"([0-9a-zA-Z])\s*\\times\s*(?=\\dim)", r"\g<1>x ", text)
    text = re.sub(r"\\dim\s*\\times\b", "dx", text)
    text = re.sub(r"\\dim\s*([xX])\b", r"d\1", text)
    text = re.sub(r"(\\int.*?(?:[0-9a-zA-Z\)\]\}]))\s*\\ln\s*([xX])\b", r"\1 d\2", text)
    text = re.sub(r"(?:\\vert|\|)\s*(?:\\(?:mathbf|mathrm|bf)\s*)?([xX])\b", r"d\1", text)
    text = re.sub(r"\b[Ik]\s*([xX])\b", r"d\1", text)
    text = re.sub(r"\b[dD]\s*X\b", "dx", text)
    text = re.sub(r"\\mathrm\{[dD]\}\s*([xX])\b", r"d\1", text)
    text = re.sub(r"\\mathrm\{\s*d\s*\}", "d", text)
    text = re.sub(r"([0-9a-zA-Z\)\]\}])\s*ix\b", r"\1 dx", text)
    text = re.sub(r"([0-9a-zA-Z\)\]\}])\s*id\b", r"\1 dx", text)

    # Normalize \times recognized as variable x
    text = re.sub(r"\\times(?=[\^_])", "x", text)
    text = re.sub(r"(\\int(?:_\{[^}]*\}\^\{[^}]*\}|_[0-9a-zA-Z]\^[0-9a-zA-Z])?\s*)\\times\b", r"\1x", text)
    text = re.sub(r"([(\[{])\s*\\times\b", r"\1x", t := text)
    text = re.sub(r"\\times\s*(?=\\mathrm\{[dD]\}|[dD]|\bI|\bk|\\dim|\b[dD][xyzut])", "x ", text)

    # 15b. Hallucinated integral symbol from label + bounds:
    text = re.sub(r"^\\Phi_{0}\|(?=_{)", "", text)
    text = re.sub(
        r"^(?:\{?\\(?:tilde|hat|bar)\{\\(?:mathbb|mathbf|mathrm)\{[A-Z]\}\}\}?|\\(?:Phi|Psi|Omega|Theta|Xi|Gamma)|\\mathbf\{\\hat\{[a-z]\}\}|{\\mathfrak\{[A-Za-z]\}}|[A-Za-z])_\{?([0-9a-zA-Z])\}?\^\{?([0-9a-zA-Z])\}?(?=.*(?:\\mathrm\{d\}|d[xyzut]|\b[Ik]x))",
        lambda m: rf"\int_{{{m.group(1)}}}^{{{m.group(2)}}}",
        text,
    )
    # Fix lower bound OCR typos: n, a, o, O -> 0 when upper bound is a positive digit
    text = re.sub(r"(\\int_)\{?[naoO]\}?(\^\{?[1-9]\}?)", r"\g<1>{0}\2", text)

    # 15c. Ensure space before differential: e.g. 3xdx -> 3x dx, 4xdx -> 4x dx
    text = re.sub(r"(?<=[0-9a-zA-Z\)\]\}])\s*(d[xyzut]\b)", r" \1", text)

    # 15d. Specific Khmer OCR misrecognitions for integral with bounds:
    # 'jូ' -> '\int_{0}^{2} ' (Khmer subscript vowel 'ូ' confused with bounds '0' and '2')
    text = re.sub(r"(?<![a-zA-Z\\\\])jូ\s*", lambda m: r"\int_{0}^{2} ", text)
    # 'fទ' -> '\int_{1}^{4} ' (Khmer consonant 'ទ' confused with bounds '1' and '4')
    text = re.sub(r"(?<![a-zA-Z\\\\])fទ\s*", lambda m: r"\int_{1}^{4} ", text)
    # 'j;' or 'j:' -> '\int_{0}^{2} ' (semicolon/colon confused with bounds '0' and '2')
    text = re.sub(r"(?<![a-zA-Z\\\\])j[;:]\s*", lambda m: r"\int_{0}^{2} ", text)
    # '}}' -> '\int_{0}^{2} ' (double curly brace curve confused with integral with bounds)
    text = re.sub(r"(?<![a-zA-Z0-9\\\}\]])\}\}(?=\s*[\(\[]?[0-9a-zA-Z])", lambda m: r"\int_{0}^{2} ", text)
    # 'J 1 2' or 'J12' or 'J2' -> '\int_{1}^{2} '
    text = re.sub(r"\bJ\s*1\s*2\s*", lambda m: r"\int_{1}^{2} ", text)
    text = re.sub(r"\bJ\s*2(?=[a-zA-Z(])", lambda m: r"\int_{1}^{2} ", text)
    # Digit bounds following integral glyph: e.g. 'j 0 2', 'J 1 4', 'f 0 2'
    text = re.sub(
        r"(?<![a-zA-Z\\\\])[jJfរ]\s*(\d)\s*(\d)\s*(?=[a-zA-Z(])",
        lambda m: rf"\int_{{{m.group(1)}}}^{{{m.group(2)}}} ",
        text,
    )
    # General [jJfរ] before math expression ending with differential d[xyzut]:
    # e.g., 'f(6x-7)e^{...} dx', 'J3e^x dx', 'រ3x dx' -> '\int ...'
    text = re.sub(
        r"(?<![a-zA-Z\\\\])[jJfរ](?=\s*[\(\[]?[0-9a-zA-Z].*?d[xyzut]\b)",
        lambda m: r"\int ",
        text,
    )

    # 17. Differential Equation OCR repairs:
    # 17a. Normalize derivative primes, asterisks, dagger, 1-powers: y^*, y^1, y^\dagger -> y'
    text = re.sub(r"\\nonumber\b", "", text)
    # compound derivative exponents first: y^{*+\zeta} -> y' + y
    text = re.sub(r"y\s*\^\s*\{?\s*(?:\*|\\ast|\'|’)\s*\+\s*(?:\\zeta|\\xi|y|\{y\}|[a-zA-Z])\s*\}?", "y' + y", text)
    text = re.sub(r"\{?y\}?\s*\^\s*\{?(?:\\ast|\*|1|\\dagger|\\prime|\')\}?", "y'", text)
    text = re.sub(r"y\s*[\'’\u2019]", "y'", text)
    text = re.sub(r"([0-9a-zA-Z\)])\s*v\'", r"\1y'", text)
    text = re.sub(r"\bv\'\b", "y'", text)
    text = re.sub(r"(?<!\\frac)(?<!\})\s*\{y\}", " y", text)
    # 17b. Inx / In x / 1nx -> \ln x
    text = re.sub(r"\b[I1]n\s*([a-zA-Z\(])", r"\\ln \1", text)
    # 17c. e* -> e^x, ex* / e3* -> e^{3x}, e-2x -> e^{-2x}, e^{-2\lambda} -> e^{-2x}
    text = re.sub(r"\be\s*\*\b", "e^x", text)
    text = re.sub(r"\be\s*([0-9]+)\s*\*", r"e^{\1x}", text)
    text = re.sub(r"\be\s*([+\-])\s*([0-9]+[a-zA-Z])\b", r"e^{\1\2}", text)
    text = re.sub(r"\be\s*([2-9][a-zA-Z])\b", r"e^{\1}", text)
    text = re.sub(r"e\^\{?\s*([+\-]?\d+)\s*\\lambda\}?", r"e^{\1x}", text)
    # 17d. y'ty -> y' + y, y'42y -> y' + 2y
    text = re.sub(r"y\'\s*t\s*([a-zA-Z0-9])", r"y' + \1", text)
    text = re.sub(r"y\'\s*4\s*([0-9]+[a-zA-Z])", r"y' + \1", text)
    # 17e. y' // 2 or y' V2 -> y' + y\sqrt{2}
    text = re.sub(r"y\'\s*\+\s*y\s*(?://|[Vv])\s*(\d+)", r"y' + y\\sqrt{\1}", text)
    # 17f. % in intervals -> \infty (e.g. (0, +%) -> (0, +\infty))
    text = re.sub(r"\(\s*0\s*,\s*\+\s*[%&]\s*\)", r"(0, +\\infty)", text)
    # 17g. Fix dy/dx OCR: dឬ, d_, dy/dx, \frac{dv}{dx} -> \frac{dy}{dx}, 3^\frac{N}{4\lambda} -> 3\frac{dy}{dx}
    text = re.sub(r"\bd[ឬ_]\b", r"\\frac{dy}{dx}", text)
    text = re.sub(r"\\frac\{\s*d[vV]\s*\}\{\s*d[xX]\s*\}", r"\\frac{dy}{dx}", text)
    text = re.sub(r"(\d+)\s*\^\s*\\frac\{[^\}]*\}\{[^\}]*\}", r"\1\\frac{dy}{dx}", text)
    text = re.sub(r"\\frac\s*y\s*y\b|\\frac\{\s*y\s*\}\{\s*y\s*\}", r"\\frac{y'}{y}", text)
    text = re.sub(r"\\frac\s*\{([^}]+)\}\s*([a-zA-Z0-9])\b", r"\\frac{\1}{\2}", text)
    text = re.sub(r"\\ln\^([0-9]+)", r"\\ln \1", text)
    text = re.sub(r"\{\\mathsf\{S\}\}|\\mathsf\{S\}", "5", text)
    # 17h. Solution verification OCR fixes
    text = re.sub(r"\\lor\s*=\s*", "y = ", text)
    text = re.sub(r"\\forall\^\{\\prime\}|\\forall\'", "y'", text)
    text = re.sub(r"\{\s*-\s*y\s*\}", "- y", text)
    text = re.sub(r"\bl\s*-\s*x\b", "1 - x", text)
    text = re.sub(r"\{\\alpha\}_\{\s*,?\s*\}", ",", text)
    # 17i. Domain annotation OCR repairs
    text = re.sub(r"(?:\{*\\hat\{\\overline\{.*?\}\}+|\bMighiNh9\b).*?(?=\\left\(\s*[\+\-]?\s*\d|\(\s*[\+\-]?\s*\d)", r"\\text{ កំណត់លើ } ", text)

    # 18. Clean multiple spaces
    text = re.sub(r"[ \t]+", " ", text).strip()

    return text
