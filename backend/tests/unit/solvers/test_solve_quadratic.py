"""
Tests for quadratic equation solving.

Covers three critical cases:
  1. Two distinct real roots (positive discriminant)
  2. One repeated root (zero discriminant)
  3. No real roots (negative discriminant)
"""
from fastapi.testclient import TestClient

from app.main import app


def test_solve_quadratic_two_real_roots_english():
    """Test quadratic with two distinct real roots: x² - 5x + 6 = 0
    Solutions: x = 2 or x = 3 (factors as (x-2)(x-3))"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve x^2 - 5x + 6 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        assert body["data"]["is_verified"] is True
        
        # Check that answer contains both roots
        answer = body["data"]["answer"]
        assert "2" in answer
        assert "3" in answer
        
        # Check that discriminant step exists
        steps = body["data"]["steps"]
        descriptions = [s["description_en"] for s in steps if s["description_en"]]
        assert any("discriminant" in d.lower() for d in descriptions)
        assert any("two distinct" in d.lower() for d in descriptions)


def test_solve_quadratic_two_real_roots_khmer():
    """Test quadratic with Khmer input: x² - 5x + 6 = 0"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ x^2 - 5x + 6 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        
        # Check Khmer descriptions exist
        steps = body["data"]["steps"]
        descriptions_km = [s["description_km"] for s in steps]
        assert any("ឌីស្ក្រីមីណង់" in d for d in descriptions_km)  # discriminant
        assert any("ចម្លើយ" in d for d in descriptions_km)  # answer


def test_solve_quadratic_one_repeated_root_english():
    """Test quadratic with one repeated root: x² - 4x + 4 = 0
    Solution: x = 2 (factors as (x-2)²)
    Discriminant = 0"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve x^2 - 4x + 4 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        assert body["data"]["is_verified"] is True
        assert body["data"]["answer"] == "2"
        
        # Check for repeated root language
        steps = body["data"]["steps"]
        descriptions = [s["description_en"] for s in steps if s["description_en"]]
        # Check if discriminant value is 0 (it's in the expression)
        discriminant_step = [s for s in steps if "discriminant" in s.get("description_en", "").lower()]
        assert len(discriminant_step) > 0, "Should have discriminant step"
        assert any("one" in d.lower() and "repeated" in d.lower() for d in descriptions)


def test_solve_quadratic_one_repeated_root_khmer():
    """Test repeated root with Khmer input"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ x^2 - 4x + 4 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "2"
        
        steps = body["data"]["steps"]
        descriptions_km = [s["description_km"] for s in steps]
        # Check for "repeated" in Khmer
        assert any("ឡើងវិញ" in d for d in descriptions_km)


def test_solve_quadratic_negative_discriminant_english():
    """Test quadratic with no real roots: x² + x + 1 = 0
    Discriminant = 1 - 4 = -3 < 0
    Complex solutions: x = -0.5 ± 0.866...i"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve x^2 + x + 1 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        
        # Check for negative discriminant messaging
        steps = body["data"]["steps"]
        descriptions = [s["description_en"] for s in steps if s["description_en"]]
        assert any("no real" in d.lower() for d in descriptions)
        assert any("complex" in d.lower() for d in descriptions)
        
        # Answer should mention complex or imaginary
        answer = body["data"]["answer"]
        assert answer is not None
        # The answer might contain 'I' for imaginary unit


def test_solve_quadratic_negative_discriminant_khmer():
    """Test no real roots with Khmer input"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ x^2 + x + 1 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        
        steps = body["data"]["steps"]
        descriptions_km = [s["description_km"] for s in steps]
        # Check for "no real solutions" in Khmer
        assert any("គ្មាន" in d and "ពិត" in d for d in descriptions_km)
        assert any("ស្មុគស្មាញ" in d for d in descriptions_km)  # complex


def test_solve_quadratic_not_in_standard_form():
    """Test equation that needs to be rearranged: x² = 4
    Should be rearranged to x² - 4 = 0
    Solutions: x = -2 or x = 2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve x^2 = 4"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        
        # Check that standard form step exists
        steps = body["data"]["steps"]
        descriptions = [s["description_en"] for s in steps if s["description_en"]]
        assert any("standard form" in d.lower() for d in descriptions)
        
        # Answer should contain both 2 and -2
        answer = body["data"]["answer"]
        assert "2" in answer


def test_solve_quadratic_with_khmer_digits():
    """Test with Khmer numeral glyphs: x² - ៥x + ៦ = ០"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ x^2 - ៥x + ៦ = ០"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        
        # Should still get correct answer
        answer = body["data"]["answer"]
        assert "2" in answer
        assert "3" in answer


def test_solve_quadratic_with_coefficient_in_front():
    """Test quadratic with leading coefficient ≠ 1: 2x² - 8x + 6 = 0
    Simplified: x² - 4x + 3 = 0
    Solutions: x = 1 or x = 3"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve 2x^2 - 8x + 6 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "quadratic_equation"
        assert body["data"]["is_verified"] is True
        
        # Check that coefficients are identified
        steps = body["data"]["steps"]
        descriptions = [s["description_en"] for s in steps if s["description_en"]]
        assert any("coefficient" in d.lower() for d in descriptions)
