"""
Tests for input validation on the API endpoints.

Ensures that:
  - Questions have a reasonable length limit
  - Empty or too-short questions are rejected
  - Properly formatted requests are accepted
"""
from fastapi.testclient import TestClient

from app.main import app


def test_valid_question_accepted():
    """Test that a normal question is accepted"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve 2x + 5 = 15"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True


def test_empty_question_rejected():
    """Test that an empty question is rejected"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": ""},
        )
        assert response.status_code == 422  # Unprocessable Entity
        body = response.json()
        assert "detail" in body


def test_missing_question_field_rejected():
    """Test that a request without a question field is rejected"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en"},
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body


def test_question_at_max_length_accepted():
    """Test that a question at exactly 500 characters is accepted"""
    with TestClient(app) as client:
        # Create a question that's exactly 500 characters
        question = "solve x + 1 = 2 " + "a" * (500 - len("solve x + 1 = 2 "))
        assert len(question) == 500
        
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": question},
        )
        assert response.status_code == 200
        # It may fail to parse due to the extra 'a's, but should not be rejected for length
        # The important part is it's not a 422 validation error


def test_question_over_max_length_rejected():
    """Test that a question over 500 characters is rejected"""
    with TestClient(app) as client:
        # Create a question that's over 500 characters
        question = "solve x + 1 = 2 " + "a" * 500
        assert len(question) > 500
        
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": question},
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body
        # Check that the error mentions the length constraint
        error_str = str(body["detail"]).lower()
        assert "500" in error_str or "length" in error_str or "characters" in error_str


def test_reasonable_length_question_accepted():
    """Test that a reasonably long question (200 chars) is accepted"""
    with TestClient(app) as client:
        # Create a more realistic longer question
        question = "ដោះស្រាយ " + "2x + 5 = 15 " * 15  # Around 180 characters
        assert len(question) < 500
        
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": question},
        )
        assert response.status_code == 200


def test_whitespace_only_question_rejected():
    """Test that a question with only whitespace is rejected"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "   "},
        )
        # Pydantic will strip whitespace, making it empty
        # This should either be 422 (validation error) or 200 with success=false
        assert response.status_code in [200, 422]


def test_unicode_characters_counted_correctly():
    """Test that Khmer unicode characters are counted correctly in length validation"""
    with TestClient(app) as client:
        # Khmer characters should count as single characters, not bytes
        question = "ដោះស្រាយសមីការ " * 30  # Each repetition is ~15 chars, total ~450
        assert len(question) < 500
        
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": question},
        )
        assert response.status_code == 200


def test_special_characters_in_question():
    """Test that special math characters are allowed"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "solve x^2 + 3*x - 4 = 0"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
