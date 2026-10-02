"""
OCR Normalization - Postprocessing and error correction.

Handles:
- LaTeX normalization (\frac, \\operatorname, etc.)
- Common OCR errors (O→0, l→1, etc.)
- Operator standardization
- Whitespace cleanup
"""

from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text

__all__ = ["sanitize_ocr_math_text"]
