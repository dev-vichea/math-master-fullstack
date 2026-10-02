"""
OCR Extraction — DEPRECATED compatibility layer.

This package is kept for backward compatibility only.
New code should import from:
  - app.ocr.engines   (OCR engine implementations)
  - app.ocr.pipeline  (processing stages)
  - app.ocr.factory   (engine creation)
"""

from app.ocr.engines.base import BaseVisionEngine, MathVisionEngine, VisionResult
from app.ocr.factory import create_vision_engine, list_available_providers

__all__ = [
    "BaseVisionEngine",
    "MathVisionEngine",
    "VisionResult",
    "create_vision_engine",
    "list_available_providers",
]
