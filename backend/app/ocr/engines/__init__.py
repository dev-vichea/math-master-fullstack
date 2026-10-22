"""
OCR Engines — Individual OCR backend implementations.

Each engine implements the MathVisionEngine interface (base.py) for
detecting mathematical text from images.

Available engines:
- StubEngine: No-op placeholder for testing
- TesseractEngine: Open-source OCR via pytesseract
- KiriEngine: Custom-trained Khmer OCR
- Pix2TexEngine: LaTeX recognition via pix2tex
- UniMERNetVisionEngine: Neural mathematical expression recognition (printed & handwritten)
- TrOCRVisionEngine: Fine-tuned TrOCR model for Khmer math expressions
- MathpixEngine: Commercial math OCR API
- GoogleVisionEngine: Google Cloud Vision API
- GeminiVisionEngine: Google Gemini multimodal API
"""

from app.ocr.engines.base import BaseVisionEngine, MathVisionEngine, VisionResult
from app.ocr.engines.unimernet_engine import UniMERNetVisionEngine

__all__ = [
    "BaseVisionEngine",
    "MathVisionEngine",
    "VisionResult",
    "UniMERNetVisionEngine",
    "TrOCRVisionEngine",
]

