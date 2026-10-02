"""Normalize raw Khmer math text into a canonical form the rest of the
pipeline (intent classifier, expression extractor, parser) can rely on."""

import re
import unicodedata

from app.parser.expression_parser.digits import khmer_digits_to_arabic

# Khmer punctuation that has a direct Latin/ASCII equivalent used in math.
_PUNCTUATION_MAP = {
    "៖": ":",  # khmer colon-like punctuation (chan)
    "។": ".",  # khmer full stop (khan)
    "៕": ".",  # khmer bar khan
    "，": ",",
    "？": "?",
}


def convert_percentages_to_decimals(text: str) -> str:
    """
    Convert percentage expressions to decimal form before SymPy parsing.
    Examples:
      "20%" -> "0.20"
      "20 %" -> "0.20"
      "20ភាគរយ" -> "0.20"
      "20 ភាគរយ" -> "0.20"
      "150.5%" -> "1.505"

    Also handles common phrases like "X% of Y" -> "(X/100) * Y"
    """
    # Handle "X% of Y" or "X ភាគរយ នៃ Y" patterns
    # Match patterns like "20% of 150" or "20 ភាគរយ នៃ 150"
    text = re.sub(r"(\d+(?:\.\d+)?)\s*%\s*(?:of|នៃ)\s+", r"(\1/100)*", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+(?:\.\d+)?)\s*ភាគរយ\s*(?:of|នៃ)\s+", r"(\1/100)*", text)

    # Handle standalone percentages: "20%" -> "(20/100)" or "0.20"
    # We use (X/100) format to preserve precision with SymPy
    text = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", text)
    text = re.sub(r"(\d+(?:\.\d+)?)\s*ភាគរយ", r"(\1/100)", text)

    return text


def normalize_khmer_text(text: str) -> str:
    """
    - Unicode-normalize (NFC) so combining Khmer diacritics compare equal.
    - Convert Khmer digits to Arabic digits.
    - Map Khmer punctuation to ASCII equivalents.
    - Convert percentages to decimal/fractional form.
    - Collapse whitespace.
    """
    text = unicodedata.normalize("NFC", text).strip()
    text = khmer_digits_to_arabic(text)
    for khmer_char, latin_char in _PUNCTUATION_MAP.items():
        text = text.replace(khmer_char, latin_char)
    text = convert_percentages_to_decimals(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
