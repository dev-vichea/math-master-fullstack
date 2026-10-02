"""
OCR Layer - Optical Character Recognition for mathematical content.

This module handles:
- Image preprocessing (contrast, noise reduction, binarization)
- OCR extraction (multiple engines: Kiri, Gemini, Google Vision, Mathpix, etc.)
- OCR normalization (postprocessing and error correction)
- Document layout analysis (reading order, region classification)

Subpackages:
- engines/   — Individual OCR engine implementations
- pipeline/  — Processing stages (cache, ensemble, router, pre/postprocessor)
- layout/    — Document layout analysis
- normalization/ — OCR text correction
- preprocessing/ — Image preprocessing
"""

from app.ocr.engines.base import BaseVisionEngine, VisionResult
from app.ocr.factory import create_vision_engine, list_available_providers
from app.ocr.preprocessing.image_preprocessor import PreprocessMode, preprocess_image

__all__ = [
    "BaseVisionEngine",
    "VisionResult",
    "create_vision_engine",
    "list_available_providers",
    "preprocess_image",
    "PreprocessMode",
]
