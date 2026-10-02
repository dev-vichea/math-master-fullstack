"""
Tests for LaTeX mathematical expression parsing and solving via latex2sympy2.
"""
from fastapi.testclient import TestClient
import pytest

from app.core.khmer.extractor import extract_expression
from app.core.parser.expression_parser import parse_math_text
from app.main import app
from app.services.math_service import process_question


def test_extract_latex_fraction_equation():
    """Test extracting LaTeX fraction equations from Khmer sentences."""
    sentence = r"ដោះស្រាយសមីការ \frac{2x+5}{3} = 15"
    extracted = extract_expression(sentence)
    assert extracted == r"\frac{2x+5}{3} = 15"


def test_extract_latex_inequality():
    """Test extracting LaTeX inequality expressions."""
    sentence = r"ដោះស្រាយអសមីការ 2x \le 10"
    extracted = extract_expression(sentence)
    assert extracted == r"2x \le 10"


def test_extract_latex_square_root():
    """Test extracting LaTeX square root expressions."""
    sentence = r"រកតម្លៃ x នៃ \sqrt{x} = 4"
    extracted = extract_expression(sentence)
    assert extracted == r"\sqrt{x} = 4"


def test_parse_latex_fraction():
    """Test parsing LaTeX fraction into SymPy equation."""
    parsed = parse_math_text(r"\frac{2x+5}{3} = 15")
    assert parsed.is_equation is True
    assert len(parsed.symbols) == 1
    assert parsed.symbols[0].name == "x"


def test_solve_latex_linear_fraction():
    """Test end-to-end solving of LaTeX linear equation with fraction."""
    data = process_question(r"ដោះស្រាយ \frac{2x+5}{3} = 15")
    assert data.answer == "20"
    assert data.is_verified is True
    assert data.problem_type == "linear_equation"
    assert len(data.steps) > 0


def test_solve_latex_arithmetic_fractions():
    """Test solving LaTeX fraction arithmetic."""
    data = process_question(r"គណនា \frac{1}{2} + \frac{3}{4}")
    assert data.answer == "5/4"
    assert data.is_verified is True
    assert data.problem_type == "arithmetic_expression"


def test_solve_latex_quadratic():
    """Test solving quadratic equation with LaTeX formatting."""
    data = process_question(r"ដោះស្រាយ x^2 - 4 = 0")
    assert data.answer == "-2, 2"
    assert data.is_verified is True
    assert data.problem_type == "quadratic_equation"


def test_solve_latex_inequality_api():
    """Test API endpoint POST /api/v1/math/solve with LaTeX inequality."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/math/solve",
        json={"language": "km", "question": r"ដោះស្រាយអសមីការ 2x \le 10"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["problem_type"] == "linear_inequality"
    assert "x" in (body["data"]["answer"] or "")
