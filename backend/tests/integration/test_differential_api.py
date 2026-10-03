"""
End-to-End API integration tests for Khmer Math Lab:
Differential Equations, Math Solve, Vision OCR, and Worksheet Processing.
"""

import os
import sys
from pathlib import Path
import pytest
from starlette.testclient import TestClient

sys.path.insert(0, "backend")

from app.main import app
from app.ocr.engines.pix2tex_engine import Pix2TexVisionEngine
from app.api.v1.endpoints.vision import get_vision_engine


def test_api_health():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "healthy")


def test_api_solve_differential_equations():
    client = TestClient(app)

    # 1. Direct integration
    res1 = client.post("/api/v1/math/solve", json={"question": "ក. y'=2x^{2}-x+1"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    assert "x^{3}" in data1["data"]["answer"] or "x**3" in data1["data"]["answer"]
    assert len(data1["data"]["steps"]) > 0

    # 2. Cauchy initial value problem
    res2 = client.post("/api/v1/math/solve", json={"question": "ខ. y'=e^{2x} , y(0)=5"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert "e^{2 x}" in data2["data"]["answer"]
    assert "9/2" in data2["data"]["answer"] or r"\frac{9}{2}" in data2["data"]["answer"]

    # 3. First order linear homogeneous
    res3 = client.post("/api/v1/math/solve", json={"question": "គ. 2y'-3y=0"})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["success"] is True
    assert "e^{\\frac{3}{2} x}" in data3["data"]["answer"] or "e^{1.5" in data3["data"]["answer"] or "e^{\\frac{3 x}{2}}" in data3["data"]["answer"]

    # 4. Cauchy linear homogeneous
    res4 = client.post("/api/v1/math/solve", json={"question": "ក. - y'+2y=0 , y(3)=-2"})
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["success"] is True
    assert "- 2" in data4["data"]["answer"] or "-2" in data4["data"]["answer"]

    # 5. Solution verification
    res5 = client.post("/api/v1/math/solve", json={"question": "ក. y = x+e^{x} , y'- y= 1 - x"})
    assert res5.status_code == 200
    data5 = res5.json()
    assert data5["success"] is True
    assert "ពិត" in data5["data"]["answer"]


def test_api_glossary_endpoints():
    client = TestClient(app)

    res_cat = client.get("/api/v1/glossary/categories")
    assert res_cat.status_code == 200
    assert res_cat.json()["success"] is True

    res_terms = client.get("/api/v1/glossary?q=សមីការ")
    assert res_terms.status_code == 200
    assert res_terms.json()["success"] is True

    res_ex = client.get("/api/v1/glossary/examples")
    assert res_ex.status_code == 200
    assert res_ex.json()["success"] is True


def test_api_vision_differential_crops():
    """Test Vision endpoint using actual cropped images and Pix2Tex engine."""
    pix_engine = Pix2TexVisionEngine()
    app.dependency_overrides[get_vision_engine] = lambda: pix_engine

    client = TestClient(app)
    crops_dir = Path("backend/training/test_exercises/differentials")

    test_crops = [
        "crop_ex1_ka.png",
        "crop_ex2_kha.png",
        "crop_ex3_ko.png",
        "crop_ex4_ka.png",
        "crop_ex5_kha.png",
    ]

    for crop_name in test_crops:
        img_path = crops_dir / crop_name
        assert img_path.exists(), f"Image {crop_name} must exist"
        with open(img_path, "rb") as f:
            files = {"image": (crop_name, f, "image/png")}
            res = client.post("/api/v1/math/vision", files=files)
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True, f"Failed for {crop_name}: {data}"
            assert "answer" in data["data"]
            assert len(data["data"]["steps"]) > 0

    app.dependency_overrides.clear()


def test_api_worksheet_process_differential():
    """Test worksheet processing endpoint with multiple differential equations."""
    from app.services.worksheet_service import WorksheetProcessor, get_worksheet_processor
    from app.ocr.engines.base import VisionResult

    class DiffMockEngine:
        def detect(self, image_bytes: bytes) -> VisionResult:
            ocr_text = (
                "ចូរដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលខាងក្រោម៖\n"
                "ក. y' = 2x^2 - x + 1\n"
                "ខ. y' = e^{2x} , y(0) = 5\n"
                "គ. 2y' - 3y = 0"
            )
            return VisionResult(detected_text=ocr_text, confidence=0.98, error_message=None)

    proc = WorksheetProcessor(vision_engine=DiffMockEngine())
    app.dependency_overrides[get_worksheet_processor] = lambda: proc

    client = TestClient(app)
    files = {"image": ("dummy.png", b"fake_bytes", "image/png")}
    res = client.post("/api/v1/worksheets/process", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    ws_data = data["data"]
    assert "solutions" in ws_data
    assert len(ws_data["solutions"]) == 3
    # Check that solutions were correctly found
    assert any("x^{3}" in s.get("answer", "") or "x**3" in s.get("answer", "") for s in ws_data["solutions"])

    app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

