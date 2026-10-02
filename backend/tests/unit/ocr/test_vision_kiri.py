"""
Tests for Kiri Khmer OCR engine and Vision API integration.
"""
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ocr.engines.base import VisionResult
from app.ocr.factory import create_vision_engine, list_available_providers
from app.ocr.engines.kiri_ocr import KiriVisionEngine
from app.main import app


class FakeKiriOCR:
    """Mock Kiri OCR model for testing without requiring heavy model weights."""

    def __init__(self, return_text="ដោះស្រាយ 2x + 5 = 15", return_results=None):
        self.return_text = return_text
        self.return_results = return_results or [
            {"text": return_text, "confidence": 0.95}
        ]

    def extract_text(self, image_path: str):
        return self.return_text, self.return_results


def test_kiri_vision_engine_empty_bytes():
    """Test detect() handles empty bytes cleanly."""
    fake_ocr = FakeKiriOCR()
    engine = KiriVisionEngine(ocr_instance=fake_ocr)
    result = engine.detect(b"")

    assert result.detected_text is None
    assert result.confidence == 0.0
    assert result.error_message == "Image data is empty"


def test_kiri_vision_engine_success():
    """Test detect() with successful text extraction."""
    fake_ocr = FakeKiriOCR(
        return_text="ដោះស្រាយ 2x + 5 = 15",
        return_results=[{"text": "ដោះស្រាយ 2x + 5 = 15", "confidence": 0.98}],
    )
    engine = KiriVisionEngine(ocr_instance=fake_ocr)
    dummy_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    result = engine.detect(dummy_image_bytes)

    assert result.detected_text == "ដោះស្រាយ 2x + 5 = 15"
    assert result.confidence == pytest.approx(0.98, rel=1e-2)
    assert result.error_message is None


def test_kiri_vision_engine_no_text():
    """Test detect() when image contains no readable text."""
    fake_ocr = FakeKiriOCR(return_text="", return_results=[])
    engine = KiriVisionEngine(ocr_instance=fake_ocr)
    dummy_image_bytes = b"sample_bytes"

    result = engine.detect(dummy_image_bytes)

    assert result.detected_text is None
    assert result.confidence == 0.0
    assert "No text detected" in (result.error_message or "")


def test_kiri_vision_engine_exception_handling():
    """Test detect() handles OCR runtime errors gracefully."""
    fake_ocr = MagicMock()
    fake_ocr.extract_text.side_effect = RuntimeError("Model inference failed")
    engine = KiriVisionEngine(ocr_instance=fake_ocr)

    result = engine.detect(b"dummy_bytes")

    assert result.detected_text is None
    assert result.confidence == 0.0
    assert "Kiri OCR error: Model inference failed" in (result.error_message or "")


def test_kiri_in_provider_list():
    """Test that list_available_providers reports kiri and khmer_ocr."""
    providers = list_available_providers()
    assert "kiri" in providers
    assert "khmer_ocr" in providers


def test_create_vision_engine_kiri():
    """Test creating vision engine by name with mock import if not installed."""
    with patch("app.ocr.engines.kiri_ocr.KIRI_OCR_AVAILABLE", True):
        with patch("app.ocr.engines.kiri_ocr.OCR"):
            engine = create_vision_engine("kiri")
            assert isinstance(engine, KiriVisionEngine)

            engine_alias = create_vision_engine("khmer_ocr")
            assert isinstance(engine_alias, KiriVisionEngine)


def test_create_vision_engine_gemini():
    """Test creating Gemini vision engine by name with mocked API key."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_gemini_key"}):
        from app.ocr.engines.gemini_vision import GeminiVisionEngine
        engine = create_vision_engine("gemini")
        assert isinstance(engine, GeminiVisionEngine)


def test_vision_endpoint_solve_pipeline():
    """Test POST /api/v1/math/vision end-to-end with mock OCR."""
    client = TestClient(app)

    # Mock the vision engine detect to return a valid Khmer math question
    mock_engine = MagicMock()
    mock_engine.detect.return_value = VisionResult(
        detected_text="ដោះស្រាយ 2x + 5 = 15",
        confidence=0.96,
        error_message=None,
    )

    with patch("app.api.v1.endpoints.vision._vision_engine", mock_engine):
        # Create a mock image file
        fake_file = ("test.png", BytesIO(b"fake_image_content"), "image/png")
        response = client.post("/api/v1/math/vision", files={"image": fake_file})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"]["answer"] == "5"
        assert data["data"]["ocr_detected_text"] == "ដោះស្រាយ 2x + 5 = 15"
        assert data["data"]["ocr_confidence"] == pytest.approx(0.96, rel=1e-2)
        assert len(data["data"]["steps"]) > 0
