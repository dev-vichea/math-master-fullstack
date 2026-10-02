"""
Tests for LaTeX-OCR (pix2tex) vision engine.
"""
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from app.ocr.factory import create_vision_engine, list_available_providers
from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine


def test_pix2tex_in_available_providers():
    providers = list_available_providers()
    assert "pix2tex" in providers
    assert "latex_ocr" in providers


def test_create_pix2tex_engine():
    engine = create_vision_engine("pix2tex")
    assert isinstance(engine, Pix2TexVisionEngine)

    engine_alias = create_vision_engine("latex_ocr")
    assert isinstance(engine_alias, Pix2TexVisionEngine)


def test_pix2tex_detect_empty_bytes():
    mock_model = MagicMock()
    engine = Pix2TexVisionEngine(model_instance=mock_model)
    res = engine.detect(b"")
    assert res.detected_text is None
    assert res.error_message == "Image data is empty"


def test_pix2tex_detect_success():
    mock_model = MagicMock()
    mock_model.return_value = r"\frac{2x+5}{3} = 15"
    engine = Pix2TexVisionEngine(model_instance=mock_model)

    from PIL import Image
    buf = BytesIO()
    Image.new("RGB", (30, 30), color="white").save(buf, format="PNG")
    dummy_png = buf.getvalue()

    res = engine.detect(dummy_png)

    assert res.detected_text == r"\frac{2x+5}{3} = 15"
    assert res.confidence == 0.95
    assert res.exercise_metadata["primary_expression"] == r"\frac{2x+5}{3} = 15"
