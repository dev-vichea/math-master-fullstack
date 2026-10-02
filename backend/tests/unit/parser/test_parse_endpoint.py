"""
Tests for POST /api/v1/math/parse endpoint.
"""
from fastapi.testclient import TestClient

from app.main import app


def test_parse_valid_khmer_equation():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/parse",
            json={"language": "km", "question": "ដោះស្រាយ 2x + 5 = 15"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["detected_intent"] == "solve_equation"
        assert "2x+5=15" in data["data"]["raw_expression"]
        assert data["data"]["problem_type"] == "linear_equation"


def test_parse_valid_english_expression():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/parse",
            json={"language": "en", "question": "simplify (x + 2)*(x - 2)"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["detected_intent"] == "simplify_expression"
        assert "x" in data["data"]["normalized_expression"]


def test_parse_no_expression():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/parse",
            json={"language": "km", "question": "សួស្តី តើអ្នកសុខសប្បាយជាទេ?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No math expression detected" in data["error"]
