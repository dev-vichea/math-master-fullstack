"""
Tests for UniMERNet vision engine in Math Lab.
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from app.ocr.engines.unimernet_engine import (
    UniMERNetVisionEngine,
    clean_unimernet_output,
)
from app.ocr.factory import create_vision_engine, list_available_providers


def test_unimernet_in_available_providers():
    providers = list_available_providers()
    assert "unimernet" in providers
    assert providers["unimernet"] is True


def test_clean_unimernet_output():
    raw = r"\[ \frac { 5 } { 8 } + \frac { 1 } { 8 } = \frac { 3 } { 4 } \]"
    cleaned = clean_unimernet_output(raw)
    assert cleaned == r"\frac { 5 } { 8 } + \frac { 1 } { 8 } = \frac { 3 } { 4 }"

    display_math = r"$$ \lim_{x \to 0} \frac{\sin x}{x} $$"
    assert clean_unimernet_output(display_math) == r"\lim_{x \to 0} \frac{\sin x}{x}"


def test_unimernet_detect_empty_bytes():
    engine = UniMERNetVisionEngine.__new__(UniMERNetVisionEngine)
    res = engine.detect(b"")
    assert res.detected_text is None
    assert res.confidence == 0.0
    assert "decoding error" in res.error_message.lower()


def test_unimernet_detect_success():
    engine = UniMERNetVisionEngine.__new__(UniMERNetVisionEngine)
    engine.device = "cpu"
    engine.models_dir = "/dummy/models"

    mock_vis_processor = MagicMock()
    mock_vis_processor.return_value = MagicMock()
    engine.vis_processor = mock_vis_processor

    mock_model = MagicMock()
    mock_model.generate.return_value = {
        "pred_str": [r"\frac { 1 } { 2 } + x = 3"]
    }
    engine.model = mock_model

    buf = BytesIO()
    Image.new("RGB", (64, 64), color="white").save(buf, format="PNG")
    dummy_bytes = buf.getvalue()

    res = engine.detect(dummy_bytes)

    assert res.detected_text == r"\frac { 1 } { 2 } + x = 3"
    assert res.confidence == 0.96
    assert res.exercise_metadata["engine"] == "unimernet"
