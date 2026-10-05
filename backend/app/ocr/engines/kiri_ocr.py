"""
Kiri OCR integration (open-source, bilingual Khmer + English deep learning OCR).

Kiri OCR is a specialized, lightweight OCR library designed specifically for
English and Khmer documents. It uses a Transformer-based model with a hybrid
CTC + attention decoder, providing accurate text detection and recognition for
Khmer script without requiring external cloud services.

Setup:
1. Install Python package:
   pip install kiri-ocr

Documentation / Source:
- GitHub: https://github.com/mrrtmob/kiri-ocr
- Hugging Face: https://huggingface.co/mrrtmob/kiri-ocr
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

try:
    from kiri_ocr import OCR

    KIRI_OCR_AVAILABLE = True
except ImportError:
    OCR = None  # type: ignore[assignment]
    KIRI_OCR_AVAILABLE = False

from app.ocr.engines.base import MathVisionEngine, VisionResult


class KiriVisionEngine(MathVisionEngine):
    """
    OCR using Kiri OCR (offline, deep learning, Khmer + English native).

    Pros:
    - Native support for Khmer script (consonants, subscripts/choeng, vowels, diacritics, numerals)
    - Mixed Khmer and English math expression recognition
    - Runs locally without internet connection or cloud API costs
    - Transformer-based architecture with CTC + attention decoding
    - Privacy-friendly (data never leaves the host)

    Cons:
    - Requires PyTorch and model weights (downloaded on first run from Hugging Face)
    - Uses more memory/CPU than simple Tesseract
    """

    def __init__(
        self,
        device: str = "cpu",
        decode_method: str = "fast",
        ocr_instance: Any | None = None,
    ):
        """
        Initialize Kiri OCR engine.

        Args:
            device: Computing device ('cpu', 'mps' for Apple Silicon, or 'cuda')
            decode_method: Decoding strategy ('fast', 'accurate', or 'beam')
            ocr_instance: Optional pre-initialized OCR instance (useful for dependency injection and testing)
        """
        if not KIRI_OCR_AVAILABLE and ocr_instance is None:
            raise ImportError("kiri-ocr is required. Install it with: pip install kiri-ocr")

        self.device = device
        self.decode_method = decode_method
        self._ocr = ocr_instance

    @property
    def ocr(self) -> Any:
        """Lazy loader for the OCR model so startup is fast until first request."""
        if self._ocr is None:
            self._ocr = OCR(device=self.device, decode_method=self.decode_method)
        return self._ocr

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Use Kiri OCR to detect Khmer and mathematical text in the image.

        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)

        Returns:
            VisionResult with detected text and confidence score
        """
        if not image_bytes:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="Image data is empty",
            )

        # Preprocess image for OCR (CLAHE contrast, upscaling, denoising)
        try:
            from app.ocr.preprocessing.image_preprocessor import preprocess_image

            processed_bytes = preprocess_image(image_bytes, mode="enhanced_grayscale")
        except Exception:
            processed_bytes = image_bytes

        # Kiri OCR takes an image file path; write image bytes to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        try:
            temp_file.write(processed_bytes)
            temp_file.flush()
            temp_path = temp_file.name
        finally:
            temp_file.close()

        try:
            text, results = self.ocr.extract_text(temp_path)

            # Calculate average confidence if available in results
            avg_confidence = 0.90
            if results and isinstance(results, list):
                confs = [
                    float(item.get("confidence", 0.9))
                    for item in results
                    if isinstance(item, dict) and "confidence" in item
                ]
                if confs:
                    avg_confidence = sum(confs) / len(confs)

            raw_detected_text = (text or "").strip()

            if not raw_detected_text:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="No text detected in image",
                )

            # Postprocess math characters and Khmer numerals
            from app.parser.exercise_parser.exercise_parser import parse_exercise
            from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text

            sanitized_text = sanitize_ocr_math_text(raw_detected_text)
            parsed_exercise = parse_exercise(sanitized_text)

            metadata = {
                "exercise_title": parsed_exercise.exercise_title,
                "instruction": parsed_exercise.instruction,
                "primary_expression": parsed_exercise.primary_expression,
                "sub_exercises": [
                    {
                        "label": sub.label,
                        "raw_text": sub.raw_text,
                        "expression": sub.expression,
                        "intent": sub.intent,
                    }
                    for sub in parsed_exercise.sub_exercises
                ],
            }

            return VisionResult(
                detected_text=sanitized_text,
                confidence=avg_confidence,
                error_message=None,
                exercise_metadata=metadata,
            )

        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"Kiri OCR error: {str(e)}",
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
