"""
TrOCR Fine-Tuned Vision Engine for Math Lab.

Uses the fine-tuned TrOCR model (trained on Khmer test exercises and math notation).
"""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any

from app.ocr.engines.base import MathVisionEngine, VisionResult

try:
    import torch
    from PIL import Image
    from transformers import (
        TrOCRProcessor,
        VisionEncoderDecoderModel,
        RobertaTokenizer,
        ViTImageProcessor,
    )

    TROCR_AVAILABLE = True
except ImportError:
    TROCR_AVAILABLE = False


class TrOCRVisionEngine(MathVisionEngine):
    """
    Local TrOCR neural OCR engine fine-tuned for Khmer math expressions.
    """

    def __init__(self, model_path: str | Path | None = None, device: str | None = None):
        if not TROCR_AVAILABLE:
            raise ImportError(
                "TrOCR engine requires torch and transformers. "
                "Install with: pip install torch transformers sentencepiece"
            )

        # Default model location: fine-tuned final model if exists, otherwise base model
        default_dir = Path(__file__).resolve().parent.parent.parent.parent / "training" / "models" / "trocr-khmer-math-final"
        if model_path is None:
            if default_dir.exists():
                model_path = str(default_dir)
            else:
                model_path = "microsoft/trocr-base-printed"

        self.model_path = str(model_path)

        # Device selection: MPS (Apple Silicon) -> CUDA -> CPU
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        # Load processor & model
        try:
            self.processor = TrOCRProcessor.from_pretrained(self.model_path)
        except Exception:
            try:
                tok = RobertaTokenizer.from_pretrained(self.model_path)
            except Exception:
                tok = RobertaTokenizer.from_pretrained("roberta-large")
            img_proc = ViTImageProcessor.from_pretrained("microsoft/trocr-base-printed")
            self.processor = TrOCRProcessor(image_processor=img_proc, tokenizer=tok)

        self.model = VisionEncoderDecoderModel.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()

    def _postprocess_math(self, text: str) -> str:
        import re
        text = re.sub(r"\s+", " ", text).strip()
        # 1. Derivative notation fixes
        text = re.sub(r"\bdy_dx\b", "dy/dx", text)
        text = re.sub(r"\by''y\b", "y'/y", text)
        text = re.sub(r"\by'y\b", "y'/y", text)
        # 2. Integral notation fixes
        if text.startswith("int_") or text.startswith("int "):
            text = re.sub(r"(int_\d+\^\d+),\s*", r"\1 ", text)
            if not re.search(r"d[a-z]\b", text):
                text = text.rstrip() + " dx"
        # 3. Spacing normalization
        text = re.sub(r"\s*,\s*", ", ", text)
        text = re.sub(r"\s*=\s*", " = ", text)
        return text.strip()

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Run OCR on image bytes and extract math expression.
        """
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.to(self.device)

            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values, max_length=64)

            raw_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            text = self._postprocess_math(raw_text)

            return VisionResult(
                detected_text=text,
                confidence=0.92,
                exercise_metadata={"model": self.model_path, "device": str(self.device), "raw_text": raw_text},
            )
        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"TrOCR recognition error: {e}",
            )
