from fastapi.testclient import TestClient

from app.main import app


def test_solve_simple_linear_equation_english():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve 2x + 5 = 15"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"
        assert body["data"]["is_verified"] is True
        assert body["data"]["problem_type"] == "linear_equation"


def test_solve_simple_linear_equation_khmer():
    """This is the exact worked example from the project handoff doc:
    'ដោះស្រាយ 2x + 5 = 15' -> x = 5, with Khmer step-by-step explanation."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ 2x + 5 = 15"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"
        assert body["data"]["normalized_expression"] == "Eq(2*x + 5, 15)"

        descriptions = [s["description_km"] for s in body["data"]["steps"]]
        assert any("ចម្លើយ" in d for d in descriptions)  # "answer" step present
        assert any("ដក" in d for d in descriptions)       # "subtract" step present


def test_solve_with_khmer_digits():
    """Khmer numeral glyphs (០១២...) should be understood too."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ ២x + ៥ = ១៥"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"


def test_solve_unrecognized_input_returns_graceful_error():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "សួស្តី តើអ្នកសុខសប្បាយទេ?"},
        )
        assert response.status_code == 200  # never a 500 for bad input
        body = response.json()
        assert body["success"] is False
        assert body["error"] is not None
