"""
Unit and integration tests for Cambodian Grade 12 BacII Chapter 4 Lesson 2:
អនុគមន៍លោការីតនេពែ (Natural Logarithmic Functions).

Covers all exercises from training/test_exercises/logarithm/image.png:
- Exercise 1: រកលោការីតនេពែនៃ e (Evaluation & Properties)
- Exercise 3: រកលីមីតនៃអនុគមន៍លោការីតនេពែ (Limits at Infinity & Zero)
- Exercise 4: រកដេរីវេនៃអនុគមន៍លោការីតនេពែ (Products & Composite Derivatives)
- Exercise 5: រកដេរីវេនៃអនុគមន៍លោការីតនេពែ (Quotients & Sums)
(Note: Exercises 2 and 6 on graphing are intentionally skipped per user request)
"""

from __future__ import annotations

import pytest
import sympy
from fastapi.testclient import TestClient
from sympy import Symbol

from app.main import app
from app.parser.math_parser.expression_parser import parse_math_text
from app.services.math_service import process_question
from app.solvers.registry import get_solver


@pytest.fixture
def client():
    return TestClient(app)


# ==============================================================================
# Exercise 1: រកលោការីតនេពែនៃ e (Properties & Evaluation)
# ==============================================================================

def test_logarithm_exercise_1_sub_ka():
    r"""Exercise 1.ក: e^{\ln 7} = 7."""
    parsed = parse_math_text(r"e^{\ln 7}")
    solver = get_solver("logarithm_evaluation")
    assert solver is not None

    result = solver.solve(parsed, "logarithm_evaluation")
    assert result.answer == "7"
    assert len(result.steps) == 3
    assert result.steps[0].title_km == "កំណត់កន្សោមដើម"
    assert "e^{\\ln a} = a" in result.steps[1].title_km or "រូបមន្តលក្ខណៈ" in result.steps[1].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_logarithm_property_exp"


def test_logarithm_exercise_1_sub_kha():
    r"""Exercise 1.ខ: \ln e^{x - 2} = x - 2."""
    parsed = parse_math_text(r"\ln(e^{x - 2})")
    solver = get_solver("logarithm_evaluation")
    assert solver is not None

    result = solver.solve(parsed, "logarithm_evaluation")
    assert result.answer == "x - 2"
    assert len(result.steps) == 3

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_logarithm_property_log_exp"


def test_logarithm_exercise_1_sub_ko():
    r"""Exercise 1.គ: \ln e^{7x} = 7x."""
    parsed = parse_math_text(r"\ln(e^{7x})")
    solver = get_solver("logarithm_evaluation")
    assert solver is not None

    result = solver.solve(parsed, "logarithm_evaluation")
    assert result.answer == "7*x"
    assert len(result.steps) == 3

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_logarithm_property_log_exp"


# ==============================================================================
# Exercise 3: រកលីមីតនៃអនុគមន៍លោការីតនេពែ (Limits)
# ==============================================================================

def test_logarithm_limit_exercise_3_sub_ka():
    r"""Exercise 3.ក: \lim_{x \to +\infty} x^{-5} \ln x = 0."""
    parsed = parse_math_text(r"\lim_{x \to +\infty} x^{-5} \ln x")
    solver = get_solver("calculus_limit")
    assert solver is not None

    result = solver.solve(parsed, "calculus_limit")
    assert result.answer == "0"
    assert len(result.steps) == 4

    # Check pedagogical steps
    assert "កំណត់កន្សោមលីមីតដើម" in result.steps[0].title_km
    assert "កំណត់រាងមិនកំណត់ [∞/∞]" in result.steps[1].title_km
    assert "អនុវត្តរូបមន្តលីមីតគ្រឹះលោការីតត្រង់អនន្ត" in result.steps[2].title_km
    assert "សន្និដ្ឋានតម្លៃលីមីតចុងក្រោយ" in result.steps[3].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_limit_logarithm_infinity"


def test_logarithm_limit_exercise_3_sub_kha():
    r"""Exercise 3.ខ: \lim_{x \to +\infty} \frac{1 + \ln x}{x^2} = 0."""
    parsed = parse_math_text(r"\lim_{x \to +\infty} \frac{1 + \ln x}{x^2}")
    solver = get_solver("calculus_limit")
    assert solver is not None

    result = solver.solve(parsed, "calculus_limit")
    assert result.answer == "0"
    assert len(result.steps) == 4

    # Check splitting terms step
    assert "បំបែកកន្សោម" in result.steps[2].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_limit_logarithm_infinity"


def test_logarithm_limit_exercise_3_sub_ko():
    r"""Exercise 3.គ: \lim_{x \to 0} (x \ln x) = 0."""
    parsed = parse_math_text(r"\lim_{x \to 0} (x \ln x)")
    solver = get_solver("calculus_limit")
    assert solver is not None

    result = solver.solve(parsed, "calculus_limit")
    assert result.answer == "0"
    assert len(result.steps) == 4

    # Check 0 x (-oo) indeterminate form
    assert "0 × (-∞)" in result.steps[1].title_km
    assert "អនុវត្តរូបមន្តលីមីតគ្រឹះលោការីតត្រង់ 0⁺" in result.steps[2].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_limit_logarithm_zero"


# ==============================================================================
# Exercise 4: រកដេរីវេនៃអនុគមន៍លោការីតនេពែ
# ==============================================================================

def test_logarithm_derivative_exercise_4_sub_ka():
    r"""Exercise 4.ក: y = \sqrt{x} \cdot \ln x -> y' = \frac{\ln x + 2}{2\sqrt{x}}."""
    parsed = parse_math_text(r"y = \sqrt{x} \cdot \ln x")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = (sympy.log(x) + 2) / (2 * sympy.sqrt(x))
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: logarithm product
    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_derivative_logarithm_product"


def test_logarithm_derivative_exercise_4_sub_kha():
    r"""Exercise 4.ខ: y = x \sqrt[3]{\ln x} -> y' = \frac{3\ln x + 1}{3\sqrt[3]{\ln^2 x}}."""
    parsed = parse_math_text(r"y = x \sqrt[3]{\ln x}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = (3 * sympy.log(x) + 1) / (3 * sympy.log(x) ** (sympy.Rational(2, 3)))
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_derivative_logarithm_product"


def test_logarithm_derivative_exercise_4_sub_ko():
    r"""Exercise 4.គ: y = \ln(x + \sqrt{1 + x^2}) -> y' = \frac{1}{\sqrt{1 + x^2}}."""
    parsed = parse_math_text(r"y = \ln(x + \sqrt{1 + x^2})")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = 1 / sympy.sqrt(x**2 + 1)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_derivative_logarithm_composite"


# ==============================================================================
# Exercise 5: រកដេរីវេនៃអនុគមន៍លោការីតនេពែ
# ==============================================================================

def test_logarithm_derivative_exercise_5_sub_ka():
    r"""Exercise 5.ក: y = \ln\frac{e^x}{e^x + 1} -> y' = \frac{1}{e^x + 1}."""
    parsed = parse_math_text(r"y = \ln\frac{e^x}{e^x + 1}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = 1 / (sympy.exp(x) + 1)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_derivative_logarithm_composite"


def test_logarithm_derivative_exercise_5_sub_kha():
    r"""Exercise 5.ខ: y = x \ln x - x -> y' = \ln x."""
    parsed = parse_math_text(r"y = x \ln x - x")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = sympy.log(x)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0


def test_logarithm_derivative_exercise_5_sub_ko():
    r"""Exercise 5.គ: y = x^2 \ln\frac{1}{x^2} -> y' = 2x(\ln(1/x^2) - 1)."""
    parsed = parse_math_text(r"y = x^2 \ln\frac{1}{x^2}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    x = Symbol("x")
    expected = 2 * x * (sympy.log(1 / (x**2)) - 1)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    assert result.lesson_info is not None
    assert result.lesson_info["lesson_id"] == "lesson_natural_logarithm"
    assert result.lesson_info["method_id"] == "method_derivative_logarithm_product"


# ==============================================================================
# End-to-End Service & API Integration Tests
# ==============================================================================

def test_logarithm_e2e_process_question_evaluation():
    r"""Test process_question for e^{\ln 7}."""
    res = process_question(r"e^{\ln 7}")
    assert res.answer == "7"
    assert res.lesson_info is not None
    assert "មេរៀនទី២ : អនុគមន៍លោការីតនេពែ" in res.lesson_info["lesson_km"]


def test_logarithm_e2e_process_question_limit():
    r"""Test process_question for \lim_{x \to +\infty} x^{-5} \ln x."""
    res = process_question(r"\lim_{x \to +\infty} x^{-5} \ln x")
    assert res.answer == "0"
    assert res.problem_type == "calculus_limit"
    assert res.lesson_info is not None
    assert "មេរៀនទី២ : អនុគមន៍លោការីតនេពែ" in res.lesson_info["lesson_km"]


def test_logarithm_e2e_process_question_derivative():
    r"""Test process_question for គណនាដេរីវេនៃអនុគមន៍ y = \sqrt{x} \cdot \ln x."""
    res = process_question(r"គណនាដេរីវេនៃអនុគមន៍ y = \sqrt{x} \cdot \ln x")
    assert res.problem_type == "calculus_derivative"
    assert res.lesson_info is not None
    assert "មេរៀនទី២ : អនុគមន៍លោការីតនេពែ" in res.lesson_info["lesson_km"]


def test_logarithm_api_solve_endpoint(client):
    r"""Test POST /api/v1/math/solve with natural logarithm limit."""
    resp = client.post("/api/v1/math/solve", json={"question": r"\lim_{x \to 0} (x \ln x)"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["answer"] == "0"
    assert data["problem_type"] == "calculus_limit"
    assert len(data["steps"]) == 4
    assert data["lesson_info"] is not None
    assert data["lesson_info"]["method_id"] == "method_limit_logarithm_zero"
