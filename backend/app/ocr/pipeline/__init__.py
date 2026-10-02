"""
OCR Pipeline — Processing stages for OCR results.

Stages:
- preprocessor: Image cleanup and enhancement before OCR
- postprocessor: Text correction and normalization after OCR
- ensemble: Multi-engine voting for higher accuracy
- router: Intelligent engine selection based on input characteristics
- cache: OCR result caching to avoid redundant processing
"""

from app.ocr.pipeline.cache import CachedOCREngine
from app.ocr.pipeline.ensemble import create_ocr_ensemble

__all__ = [
    "CachedOCREngine",
    "create_ocr_ensemble",
]
