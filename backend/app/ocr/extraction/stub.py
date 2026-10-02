from app.ocr.extraction.base import MathVisionEngine, VisionResult


class NotImplementedVisionEngine(MathVisionEngine):
    """Wires up the /math/vision endpoint now (so the Flutter camera flow
    can be built and tested against a real, stable contract today) while
    the actual OCR model is developed in a later phase."""

    def detect(self, image_bytes: bytes) -> VisionResult:
        return VisionResult(
            detected_text=None,
            confidence=0.0,
            error_message=(
                "Math Vision is not implemented yet. This endpoint is "
                "wired up so the mobile app can integrate against the "
                "final contract now; OCR will be added in a later "
                "development phase without changing this endpoint's shape."
            ),
        )
