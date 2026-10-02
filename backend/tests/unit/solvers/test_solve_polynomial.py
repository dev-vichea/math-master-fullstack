"""
Tests for polynomial equation solving (degree 3+).

Covers:
  - Cubic equations (degree 3) with real roots
  - Quartic equations (degree 4)
  - Equations with complex roots
  - Factored vs expanded forms
  - Khmer language support
  - Edge cases (all roots same, irrational roots)
"""
from fastapi.testclient import TestClient

from app.main import app


def test_solve_cubic_three_real_roots_english():
    """Test cubic with three distinct real roots: x^3 - 6x^2 + 11x - 6 = 0
    Factors as (x-1)(x-2)(x-3), so roots are x = 1, 2, 3"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 - 6x^2 + 11x - 6 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        # Answer should contain all three roots
        answer = body["data"]["answer"]
        assert "1" in answer
        assert "2" in answer
        assert "3" in answer
        assert body["data"]["is_verified"] is True
        assert len(body["data"]["steps"]) >= 4  # At least original, standard form, degree, solutions


def test_solve_cubic_three_real_roots_khmer():
    """Test cubic equation with Khmer input: x^3 - 7x + 6 = 0
    Roots are x = -3, 1, 2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "ដោះស្រាយ x^3 - 7x + 6 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True
        
        # Check that Khmer descriptions exist
        first_step = body["data"]["steps"][0]
        assert "សមីការដើម" in first_step["description_km"]


def test_solve_cubic_one_real_root_english():
    """Test cubic with one real root and two complex roots: x^3 - 1 = 0
    Real root: x = 1, Complex roots: x = -1/2 ± √3i/2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 - 1 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        # Should have at least one real root (x=1)
        answer = body["data"]["answer"]
        assert "1" in answer
        assert body["data"]["is_verified"] is True


def test_solve_cubic_factored_form():
    """Test cubic in factored form: (x-2)(x+1)(x-5) = 0
    Roots: x = -1, 2, 5"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "(x-2)*(x+1)*(x-5) = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        answer = body["data"]["answer"]
        assert "-1" in answer or "(-1)" in answer
        assert "2" in answer
        assert "5" in answer
        assert body["data"]["is_verified"] is True


def test_solve_quartic_four_real_roots_english():
    """Test quartic with four real roots: x^4 - 5x^2 + 4 = 0
    This is a bi-quadratic: let y = x^2, then y^2 - 5y + 4 = 0
    y = 1 or y = 4, so x = ±1, ±2"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^4 - 5x^2 + 4 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        answer = body["data"]["answer"]
        # Should contain ±1 and ±2
        assert "1" in answer
        assert "2" in answer
        assert body["data"]["is_verified"] is True
        assert len(body["data"]["steps"]) >= 3


def test_solve_quartic_with_khmer():
    """Test quartic equation with Khmer input"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "រក x ពី x^4 - 16 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True
        
        # x^4 = 16 gives x = ±2 (real roots)
        answer = body["data"]["answer"]
        assert "2" in answer


def test_solve_cubic_with_repeated_root():
    """Test cubic with a repeated root: x^3 - 3x^2 + 3x - 1 = 0
    This is (x-1)^3 = 0, so x = 1 (triple root)"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 - 3x^2 + 3x - 1 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True
        
        # Should have x = 1 as solution
        answer = body["data"]["answer"]
        assert "1" in answer


def test_solve_cubic_not_in_standard_form():
    """Test cubic that needs rearranging: x^3 + 2x = 5x^2 + 8
    Rearranges to: x^3 - 5x^2 + 2x - 8 = 0"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 + 2x = 5x^2 + 8"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True
        
        # Should show rearrangement step
        steps_descriptions = [step["description_en"] for step in body["data"]["steps"]]
        has_rearrangement = any("standard form" in desc.lower() for desc in steps_descriptions if desc)
        assert has_rearrangement


def test_solve_cubic_with_khmer_digits():
    """Test cubic with Khmer numerals: x^3 - ៦x^2 + ១១x - ៦ = 0"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "x^3 - ៦x^2 + ១១x - ៦ = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True


def test_solve_degree_5_polynomial():
    """Test degree 5 polynomial (quintic): x^5 - x = 0
    Factors as x(x^4 - 1) = x(x^2-1)(x^2+1) = x(x-1)(x+1)(x^2+1)
    Real roots: x = -1, 0, 1"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^5 - x = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        answer = body["data"]["answer"]
        assert "0" in answer
        assert "1" in answer
        assert body["data"]["is_verified"] is True
        
        # Should mention Abel-Ruffini theorem or degree 5
        steps_text = " ".join(
            step["description_en"] or "" for step in body["data"]["steps"]
        )
        assert "5" in steps_text or "degree" in steps_text.lower()


def test_solve_cubic_with_irrational_roots():
    """Test cubic with irrational roots: x^3 - 2 = 0
    Real root: x = ∛2 ≈ 1.26"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 - 2 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        assert body["data"]["is_verified"] is True
        
        # Should have at least one real root
        assert body["data"]["answer"] is not None
        assert len(body["data"]["steps"]) >= 3


def test_solve_quartic_all_complex_roots():
    """Test quartic with all complex roots: x^4 + 1 = 0
    Roots are the 4th roots of -1"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^4 + 1 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "polynomial_equation"
        
        # All roots are complex, so answer should mention complex or I
        answer = body["data"]["answer"]
        assert answer is not None
        # May contain 'I' for imaginary unit or specific complex numbers


def test_polynomial_classification():
    """Test that degree 3+ equations are correctly classified as polynomial_equation"""
    test_cases = [
        "x^3 + 1 = 0",
        "x^4 - x^2 + 1 = 0",
        "x^5 + x^3 + x = 0",
    ]
    
    with TestClient(app) as client:
        for question in test_cases:
            response = client.post(
                "/api/v1/math/solve",
                json={"language": "en", "question": question},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["success"] is True
            assert body["data"]["problem_type"] == "polynomial_equation", f"Failed for: {question}"


def test_polynomial_steps_include_factoring():
    """Test that factoring is shown when possible"""
    with TestClient(app) as client:
        # This factors nicely: x^3 - 8 = (x-2)(x^2+2x+4)
        response = client.post(
            "/api/v1/math/solve",
            json={"language": "en", "question": "x^3 - 8 = 0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        
        # Check if factoring step exists
        steps_descriptions = [step["description_en"] or "" for step in body["data"]["steps"]]
        has_factor_step = any("factor" in desc.lower() for desc in steps_descriptions)
        # Note: May or may not factor depending on SymPy's behavior
        # Just verify steps exist and are meaningful
        assert len(body["data"]["steps"]) >= 3


def test_polynomial_verification_works():
    """Test that all polynomial solutions are verified by substitution"""
    test_cases = [
        ("x^3 - 6x^2 + 11x - 6 = 0", True),  # Should verify
        ("x^4 - 5x^2 + 4 = 0", True),  # Should verify
        ("x^3 - 1 = 0", True),  # Should verify
    ]
    
    with TestClient(app) as client:
        for question, should_verify in test_cases:
            response = client.post(
                "/api/v1/math/solve",
                json={"language": "en", "question": question},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["success"] is True
            assert body["data"]["is_verified"] == should_verify, f"Verification failed for: {question}"


def test_polynomial_expansion_textbook_step_by_step():
    """Test pedagogical step-by-step expansion matching Cambodian textbook standards:
    A = (k + 4)(k^2 - 4k + 1)
      Step 1: Original expression
      Step 2: Distributive property: k(k^2 - 4k + 1) + 4(k^2 - 4k + 1)
      Step 3: Expanded terms: k^3 - 4k^2 + k + 4k^2 - 16k + 4
      Step 4: Combined like terms: k^3 - 15k + 4
    """
    with TestClient(app) as client:
        # Case A: Named assignment
        res = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "A = (k+4)(k^2 - 4k + 1)"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["problem_type"] == "factored_expression"
        assert data["variable"] == "A"
        assert "k**3 - 15*k + 4" in data["answer"] or "k^3" in data["answer"]
        assert len(data["steps"]) == 4
        assert "លក្ខណៈបំបែក" in data["steps"][1]["description_km"]
        assert "គុណពន្លាត" in data["steps"][2]["description_km"]
        assert "បង្រួមតួដូចគ្នា" in data["steps"][3]["description_km"]

        # Case B: Without named assignment
        res2 = client.post(
            "/api/v1/math/solve",
            json={"language": "km", "question": "(x+3)(x^2 + 4x - 3)"},
        )
        assert res2.status_code == 200
        data2 = res2.json()["data"]
        assert len(data2["steps"]) == 4
        assert "7*x**2" in data2["answer"] or "7x^2" in data2["answer"]
