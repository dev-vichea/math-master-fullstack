"""
Pluggable interface for Math Vision (image -> math text). A real
implementation (OCR model, fine-tuned vision-language model, etc.) will
implement this interface later; the API endpoint and the rest of the
pipeline downstream of it (parser -> engine -> Khmer explanation) do not
need to change when that happens.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class VisionResult:
    detected_text: str | None
    confidence: float
    error_message: str | None = None
    exercise_metadata: dict[str, Any] | None = None


class MathVisionEngine(ABC):
    @abstractmethod
    def detect(self, image_bytes: bytes) -> VisionResult: ...


# Convenient alias
BaseVisionEngine = MathVisionEngine
