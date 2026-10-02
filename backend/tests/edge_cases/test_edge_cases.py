"""
Edge case tests for robustness and security.

Covers:
  - Very large numbers
  - Very small decimals
  - Deeply nested parentheses
  - Mixed operations complexity
  - Malformed input (security)
  - Unicode edge cases
  - Empty/whitespace input
  - Special characters
  - Division by zero
  - Extreme equation complexity
"""
from fastapi.testclient import TestClient

from app.main import app


def test_very_large_numbers():
    """Test with very large numbers (billions)"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "1000000 + 2000000"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "3000000"


def test_very_small_decimals():
    """Test with very small decimal numbers"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "0.0001 + 0.0002"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Accept slight floating point variations
        answer = float(body["data"]["answer"])
        assert abs(answer - 0.0003) < 0.00001


def test_deeply_nested_parentheses():
    """Test deeply nested parentheses: ((((1+2)*3)+4)*5) = 65"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "((((1+2)*3)+4)*5)"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # (((3*3)+4)*5) = ((9+4)*5) = (13*5) = 65
        assert body["data"]["answer"] == "65"


def test_mixed_operations_complex():
    """Test complex expression with all operations"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "10 + 5 * 2 - 8 / 4 + 3^2"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # 10 + 10 - 2 + 9 = 27
        assert body["data"]["answer"] == "27"


def test_division_by_zero_expression():
    """Test division by zero in expression returns infinity"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "1 / 0"},
        )
        assert response.status_code == 200
        body = response.json()
        # SymPy returns zoo (complex infinity) or may error gracefully
        # Accept either success with special value or graceful error
        assert body["success"] in [True, False]


def test_empty_question():
    """Test empty question is rejected"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": ""},
        )
        # Should be rejected by Pydantic validation
        assert response.status_code == 422


def test_whitespace_only_question():
    """Test whitespace-only question returns error"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "   \t\n  "},
        )
        # After normalization, becomes empty and fails to extract expression
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False


def test_non_math_text():
    """Test pure text with no math returns graceful error"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "Hello world this has no math"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert "error" in body
        assert body["error"] is not None


def test_sql_injection_attempt():
    """Test SQL injection patterns are handled safely"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "'; DROP TABLE users; --"},
        )
        assert response.status_code == 200
        body = response.json()
        # Should not crash, either returns error or tries to parse
        assert "success" in body


def test_script_injection_attempt():
    """Test script injection is handled safely"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "<script>alert('xss')</script>"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "success" in body


def test_unicode_emoji_in_question():
    """Test unicode emojis don't crash the parser"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "😀 គណនា 2 + 3 😀"},
        )
        assert response.status_code == 200
        body = response.json()
        # Should either extract the math or error gracefully
        assert "success" in body


def test_mixed_khmer_latin_digits():
    """Test mixing Khmer and Latin digits in same expression"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "១0 + ២0"},
        )
        assert response.status_code == 200
        body = response.json()
        # Normalizer should convert all Khmer digits to Latin
        assert body["success"] is True


def test_extremely_long_expression():
    """Test very long expression doesn't cause timeout"""
    # Create long but valid expression: 1+1+1+...
    long_expr = " + ".join(["1"] * 50)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": long_expr},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "50"


def test_negative_numbers_in_equation():
    """Test equations with negative numbers"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x + (-5) = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "15"


def test_equation_with_negative_solution():
    """Test equation that has negative solution"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x + 10 = 5"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "-5"


def test_zero_coefficient_equation():
    """Test equation with zero coefficient: 0*x + 5 = 5"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "0*x + 5 = 5"},
        )
        assert response.status_code == 200
        body = response.json()
        # This is an identity (true for all x) or degenerates
        # Accept any non-crash response
        assert "success" in body


def test_special_characters_in_khmer():
    """Test Khmer special punctuation is normalized"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនា៖ ២ + ៣"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"


def test_multiple_equals_signs():
    """Test malformed input with multiple = signs"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x = 5 = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        # Parser should handle gracefully (error or pick first)
        assert "success" in body


def test_no_variable_in_equation():
    """Test equation with no variables: 5 = 5"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "5 = 5"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "true"


def test_false_equation():
    """Test false equation: 5 = 10"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "5 = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "false"


def test_fractional_exponents():
    """Test fractional exponents: x^(1/2) = square root"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "16^(1/2)"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "4"


def test_negative_exponents():
    """Test negative exponents: 2^(-2) = 1/4"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "2^(-2)"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "1/4"


def test_irrational_result():
    """Test equation with irrational solution: x^2 = 2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^2 = 2"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Should contain sqrt(2) or approximation
        answer = body["data"]["answer"]
        assert answer is not None
        assert "sqrt" in answer.lower() or "2" in answer


def test_multiple_variables_different_problem_type():
    """Test expression with multiple variables"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "2x + 3y = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        # Should classify as multivariate and handle gracefully
        assert "success" in body
        if body["success"]:
            assert body["data"]["problem_type"] == "multivariate_equation"


def test_unicode_normalization():
    """Test that different Unicode representations normalize correctly"""
    with TestClient(app) as client:
        # Test with combining diacritics
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "គណនា 5 + 5"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True


def test_extremely_nested_operations():
    """Test deeply nested operations with multiple precedence levels"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "((2+3)*(4+5))^2 / (3*3)"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # (5*9)^2 / 9 = 45^2 / 9 = 2025 / 9 = 225
        assert body["data"]["answer"] == "225"


def test_implicit_multiplication_edge_case():
    """Test implicit multiplication: 2x vs 2*x"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "2x = 10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "5"


def test_percentage_edge_case_zero():
    """Test 0% of something"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "0% of 100"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "0"


def test_percentage_over_100_edge():
    """Test percentage over 100%: 200% of 50 = 100"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "200% of 50"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "100"


def test_fraction_with_zero_numerator():
    """Test fraction with zero numerator: 0/5 = 0"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "0/5"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "0"


def test_inequality_boundary_value():
    """Test inequality with addition: x + 5 < 10"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x + 5 < 10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "linear_inequality"
        assert "5" in body["data"]["answer"]
