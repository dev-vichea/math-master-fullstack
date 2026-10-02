"""Khmer numeral conversion. Khmer has its own digit glyphs (០-៩) that are
common in handwritten/typed Khmer math text and must be converted to Arabic
digits before any expression parser can touch them."""

KHMER_DIGITS = "០១២៣៤៥៦៧៨៩"
ARABIC_DIGITS = "0123456789"

_KHMER_TO_ARABIC = str.maketrans(KHMER_DIGITS, ARABIC_DIGITS)
_ARABIC_TO_KHMER = str.maketrans(ARABIC_DIGITS, KHMER_DIGITS)


def khmer_digits_to_arabic(text: str) -> str:
    """Convert any Khmer numeral characters in `text` to Arabic numerals."""
    return text.translate(_KHMER_TO_ARABIC)


def arabic_digits_to_khmer(text: str) -> str:
    """Convert Arabic numerals to Khmer numerals (useful when rendering a
    final answer back in a fully-Khmer style if ever needed)."""
    return text.translate(_ARABIC_TO_KHMER)
