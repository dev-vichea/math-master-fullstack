"""
Unit tests for image preprocessor (CLAHE, denoising, adaptive thresholding).
"""
import io

import pytest
from PIL import Image

from app.ocr.preprocessing.image_preprocessor import preprocess_image


def _create_dummy_image(width=400, height=100, color=(200, 200, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_preprocess_empty_bytes():
    assert preprocess_image(b"") == b""


def test_preprocess_enhanced_grayscale():
    raw_bytes = _create_dummy_image(400, 100)
    processed = preprocess_image(raw_bytes, mode="enhanced_grayscale")

    assert len(processed) > 0
    # Output should be a valid PNG image
    out_img = Image.open(io.BytesIO(processed))
    assert out_img.format == "PNG"
    # Should have been upscaled to min_dimension (800) plus padding
    assert out_img.size[1] >= 800 or out_img.size[0] >= 800


def test_preprocess_binary_mode():
    raw_bytes = _create_dummy_image(500, 120)
    processed = preprocess_image(raw_bytes, mode="binary")

    assert len(processed) > 0
    out_img = Image.open(io.BytesIO(processed))
    assert out_img.format == "PNG"


def test_preprocess_standard_mode():
    raw_bytes = _create_dummy_image(500, 120)
    processed = preprocess_image(raw_bytes, mode="standard")

    assert len(processed) > 0
    out_img = Image.open(io.BytesIO(processed))
    assert out_img.format == "PNG"
