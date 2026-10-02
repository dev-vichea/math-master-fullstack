"""
Tests for fraction and percentage operations.

Covers:
  - Basic fraction arithmetic (addition, subtraction, multiplication, division)
  - Percentage calculations (X% of Y)
  - Khmer keywords (ភាគរយ, ប្រភាគ)
  - Mixed operations
"""
from fastapi.testclient import TestClient

from app.main import app


def test_fraction_addition_english():
    """Test basic fraction addition: 3/4 + 1/2 = 5/4"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "3/4 + 1/2"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5/4"
        assert body["data"]["is_verified"] is True


def test_fraction_addition_khmer():
    """Test fraction addition with Khmer: 3/4 + 1/2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនា 3/4 + 1/2"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5/4"


def test_fraction_subtraction():
    """Test fraction subtraction: 5/6 - 1/3 = 1/2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "5/6 - 1/3"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "1/2"


def test_fraction_multiplication():
    """Test fraction multiplication: 2/3 * 3/4 = 1/2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "2/3 * 3/4"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "1/2"


def test_percentage_of_number_english():
    """Test percentage calculation: 20% of 150 = 30"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "20% of 150"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "30"


def test_percentage_of_number_khmer():
    """Test percentage with Khmer keyword: 20 ភាគរយ នៃ 150 = 30"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "20 ភាគរយ នៃ 150"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "30"


def test_percentage_calculation_25_percent():
    """Test 25% of 200 = 50"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "25% of 200"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "50"


def test_percentage_calculation_decimal():
    """Test percentage with decimal: 12.5% of 80 = 10"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "12.5% of 80"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Accept both integer and decimal representation
        answer = body["data"]["answer"]
        assert answer in ["10", "10.0", "10.0000000000000"] or float(answer) == 10.0


def test_standalone_percentage():
    """Test standalone percentage conversion: 75% = 3/4"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "75%"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Should convert to 75/100 = 3/4
        assert body["data"]["answer"] == "3/4"


def test_percentage_in_expression():
    """Test percentage in arithmetic: 50% + 25% = 3/4"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "50% + 25%"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # 50/100 + 25/100 = 3/4
        assert body["data"]["answer"] == "3/4"


def test_mixed_fraction_and_decimal():
    """Test mixed operations: 1/2 + 0.25 = 3/4 or 0.75"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "1/2 + 0.25"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Accept both fraction and decimal representation
        # 1/2 + 1/4 = 3/4 = 0.75
        answer = body["data"]["answer"]
        assert answer in ["3/4", "0.75", "0.750000000000000"] or float(answer) == 0.75


def test_complex_fraction_expression():
    """Test complex fraction: (1/2 + 1/3) * 6 = 5"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "(1/2 + 1/3) * 6"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"


def test_percentage_with_khmer_digits():
    """Test percentage with Khmer digits: ២០% នៃ ១៥០ = 30"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "២០% នៃ ១៥០"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "30"


def test_fraction_keyword_khmer():
    """Test that Khmer fraction keyword triggers correct intent"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនាប្រភាគ 2/3 + 1/6"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # 2/3 + 1/6 = 5/6
        assert body["data"]["answer"] == "5/6"
        assert body["data"]["detected_intent"] == "evaluate_expression"


def test_percentage_over_100():
    """Test percentage over 100%: 150% of 40 = 60"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "150% of 40"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "60"


def test_fraction_simplification():
    """Test that fractions are simplified: 4/8 = 1/2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "4/8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "1/2"


def test_percentage_khmer_word_only():
    """Test using only Khmer percentage word: 30 ភាគរយ = 3/10"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "30 ភាគរយ"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # 30/100 = 3/10
        assert body["data"]["answer"] == "3/10"
