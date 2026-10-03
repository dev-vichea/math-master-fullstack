"""
Tests for enriched Vision API endpoint with Khmer and English exercise metadata.
"""
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ocr.engines.base import VisionResult
from app.main import app


def test_vision_endpoint_returns_exercise_metadata():
    client = TestClient(app)

    mock_engine = MagicMock()
    mock_engine.detect.return_value = VisionResult(
        detected_text="Exercise 1: Solve for x: 3x - 9 = 0",
        confidence=0.98,
        error_message=None,
        exercise_metadata={
            "exercise_title": "Exercise 1",
            "instruction": "Solve for x",
            "primary_expression": "3x-9=0",
            "sub_exercises": [],
        },
    )

    with patch("app.api.v1.endpoints.vision._vision_engine", mock_engine):
        fake_file = ("exercise.png", BytesIO(b"fake_image_bytes"), "image/png")
        response = client.post("/api/v1/math/vision", files={"image": fake_file})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        res_data = data["data"]

        assert res_data["exercise_title"] == "Exercise 1"
        assert res_data["instruction"] == "Solve for x"
        assert res_data["cleaned_math_expression"] == "3x-9=0"
        assert res_data["answer"] == "3"
        assert res_data["ocr_detected_text"] == "Exercise 1: Solve for x: 3x - 9 = 0"
        assert res_data["ocr_confidence"] == pytest.approx(0.98, rel=1e-2)
        assert len(res_data["steps"]) > 0


def test_vision_endpoint_khmer_exercise_with_subitems():
    client = TestClient(app)

    mock_engine = MagicMock()
    mock_engine.detect.return_value = VisionResult(
        detected_text="លំហាត់ទី 1\nក. 2x + 4 = 12\nខ) 3x - 9 = 0",
        confidence=0.95,
        error_message=None,
        exercise_metadata={
            "exercise_title": "លំហាត់ទី 1",
            "instruction": None,
            "primary_expression": "2x+4=12",
            "sub_exercises": [
                {"label": "ក", "raw_text": "2x + 4 = 12", "expression": "2x+4=12", "intent": "solve_equation"},
                {"label": "ខ", "raw_text": "3x - 9 = 0", "expression": "3x-9=0", "intent": "solve_equation"},
            ],
        },
    )

    with patch("app.api.v1.endpoints.vision._vision_engine", mock_engine):
        fake_file = ("khmer_ex.png", BytesIO(b"fake_image_bytes"), "image/png")
        response = client.post("/api/v1/math/vision", files={"image": fake_file})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        res_data = data["data"]

        assert res_data["exercise_title"] == "លំហាត់ទី 1"
        assert len(res_data["sub_exercises"]) == 2
        assert res_data["sub_exercises"][0]["label"] == "ក"
        assert res_data["answer"] == "4"


def test_vision_endpoint_sample2_quadratic_equation():
    """Test that sample2.png with x^2 - 25x + 15 = 0 is solved as quadratic equation."""
    from pathlib import Path
    client = TestClient(app)

    candidates = [
        Path("frontend/samples/sample2.png"),
        Path(__file__).resolve().parent.parent.parent / "frontend" / "samples" / "sample2.png",
        Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "samples" / "sample2.png",
        Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "samples" / "sample2.png",
    ]
    sample_file = next((p for p in candidates if p.exists()), None)
    if not sample_file:
        pytest.skip("sample2.png fixture not found")

    with open(sample_file, "rb") as f:
        img_bytes = f.read()

    fake_file = ("sample2.png", BytesIO(img_bytes), "image/png")
    response = client.post("/api/v1/math/vision", files={"image": fake_file})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert res_data["problem_type"] == "quadratic_equation"
    assert "sqrt(565)" in res_data["answer"]
