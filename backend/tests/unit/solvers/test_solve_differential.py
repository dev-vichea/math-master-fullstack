"""
Unit and integration tests for Cambodian Grade 12 BacII Chapter 6:
សមីការឌីផេរ៉ង់ស្យែល (Differential Equations - First Order Form).

Covers exercises from:
- training/test_exercises/differentials/
  Exercise 1: Direct integration y' = f(x) and g(x)y' = f(x)
  Exercise 2: Direct integration with Cauchy initial conditions y(x_0) = y_0
  Exercise 3: Linear homogeneous y' + ay = 0 and Ay' + By = 0 -> y = A e^{-ax}
  Exercise 4: Linear homogeneous with Cauchy initial conditions
  Exercise 5: Verification that y = f(x) is a solution to F(x, y, y') = 0
"""

from __future__ import annotations

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.parser.math_parser.expression_parser import parse_math_text
from app.services.math_service import process_question
from app.solvers.registry import get_solver


@pytest.fixture
def client():
    return TestClient(app)


# ==============================================================================
# Exercise 1: Direct Integration (y' = f(x), g(x)y' = f(x))
# ==============================================================================

def test_differential_direct_1_ka():
    r"""Exercise 1.ក: y' = 2x^2 - x + 1 -> y = (2/3)x^3 - (1/2)x^2 + x + c."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' = 2x^2 - x + 1")
    assert parsed.is_equation is True
    result = solver.solve(parsed.sympy_expr)

    assert result is not None
    assert "x^{3}" in result.answer or "x^3" in result.answer
    assert "3" in result.answer
    assert len(result.steps) >= 2


def test_differential_direct_1_kha():
    r"""Exercise 1.ខ: y' = e^{-2x} -> y = -(1/2)e^{-2x} + c."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' = e^{-2x}")
    result = solver.solve(parsed.sympy_expr)

    assert result is not None
    assert "e^{- 2 x}" in result.answer or "e^{-2x}" in result.answer
    assert "-" in result.answer


def test_differential_direct_1_ko():
    r"""Exercise 1.គ: y' = 2x / (x^2 + 1) -> y = ln(x^2 + 1) + c."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' = \frac{2x}{x^2 + 1}")
    result = solver.solve(parsed.sympy_expr)

    assert result is not None
    assert "ln" in result.answer.lower() or "log" in result.answer.lower()


def test_differential_direct_1_kho():
    r"""Exercise 1.ឃ: y' = x / (x^2 - 1) កំណត់លើ (-1, 1)."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' = \frac{x}{x^2 - 1} \text{ កំណត់លើ } (-1, 1)")
    assert parsed.metadata.get("domain") == "(-1, 1)"
    result = solver.solve(parsed)

    assert result is not None
    assert "ln" in result.answer.lower() or "log" in result.answer.lower()
    assert any("(-1, 1)" in (s.description_km or "") for s in result.steps)


def test_differential_direct_1_ngo():
    r"""Exercise 1.ង: xy' = 1 កំណត់លើ (0, +\infty) -> y = ln(x) + c."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"xy' = 1 \text{ កំណត់លើ } (0, +\infty)")
    result = solver.solve(parsed)

    assert result is not None
    assert "ln" in result.answer.lower() or "log" in result.answer.lower()


# ==============================================================================
# Exercise 2: Direct Integration with Initial Conditions
# ==============================================================================

def test_differential_cauchy_2_ka():
    r"""Exercise 2.ក: y'/y = cos(x), y(\pi/2) = e -> y = e^{\sin x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"\frac{y'}{y} = \cos x , y(\frac{\pi}{2}) = e")
    assert parsed.metadata.get("cauchy") is not None

    result = solver.solve(parsed)
    assert result is not None
    assert "sin" in result.answer
    assert "e" in result.answer


def test_differential_cauchy_2_kha():
    r"""Exercise 2.ខ: y' = e^{2x}, y(0) = 5 -> y = (1/2)e^{2x} + 9/2."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' = e^{2x} , y(0) = 5")
    result = solver.solve(parsed)

    assert result is not None
    assert "9/2" in result.answer or r"\frac{9}{2}" in result.answer


def test_differential_cauchy_2_ko():
    r"""Exercise 2.គ: (3x^2 - 2)y' = 6x, y(1) = 4 -> y = ln|3x^2 - 2| + 4."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"(3x^2 - 2)y' = 6x , y(1) = 4")
    result = solver.solve(parsed)

    assert result is not None
    assert "ln" in result.answer.lower() or "log" in result.answer.lower()
    assert "4" in result.answer


def test_differential_cauchy_2_kho():
    r"""Exercise 2.ឃ: y' / tan(x) = 1, y(0) = 0 -> y = -ln|cos x|."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"\frac{y'}{\tan x} = 1 , y(0) = 0")
    result = solver.solve(parsed)

    assert result is not None
    assert "cos" in result.answer


# ==============================================================================
# Exercise 3: Linear Homogeneous (y' + ay = 0, Ay' + By = 0, dy/dx + ay = 0)
# ==============================================================================

def test_differential_linear_3_ka():
    r"""Exercise 3.ក: dy/dx + 2y = 0 -> y = A e^{-2x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"\frac{dy}{dx} + 2y = 0")
    result = solver.solve(parsed)

    assert result is not None
    assert "-2" in result.answer or "- 2" in result.answer
    assert "A" in result.answer
    assert any("ចំនួនថេរ" in (s.description_km or "") for s in result.steps)


def test_differential_linear_3_kha():
    r"""Exercise 3.ខ: 3 dy/dx + y = 0 -> y = A e^{-(1/3)x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"3 \frac{dy}{dx} + y = 0")
    result = solver.solve(parsed)

    assert result is not None
    assert "3" in result.answer
    assert "A" in result.answer


def test_differential_linear_3_ko():
    r"""Exercise 3.គ: 2y' - 3y = 0 -> y = A e^{(3/2)x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"2y' - 3y = 0")
    result = solver.solve(parsed)

    assert result is not None
    assert r"\frac{3}{2}" in result.answer or ("3" in result.answer and "2" in result.answer)
    assert "A" in result.answer


def test_differential_linear_3_kho():
    r"""Exercise 3.ឃ: y' + y\sqrt{2} = 0 -> y = A e^{-\sqrt{2}x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y' + y\sqrt{2} = 0")
    result = solver.solve(parsed)

    assert result is not None
    assert "sqrt" in result.answer
    assert "A" in result.answer


# ==============================================================================
# Exercise 4: Linear Homogeneous with Initial Conditions
# ==============================================================================

def test_differential_linear_cauchy_4_ka():
    r"""Exercise 4.ក: -y' + 2y = 0, y(3) = -2 -> y = -2 e^{2x - 6}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"-y' + 2y = 0 , y(3) = -2")
    result = solver.solve(parsed)

    assert result is not None
    assert "- 2" in result.answer or "-2" in result.answer
    assert "e" in result.answer


def test_differential_linear_cauchy_4_kha():
    r"""Exercise 4.ខ: 2y' + y = 0, y(\ln 4) = 1/5 -> y = (2/5) e^{-(1/2)x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"2y' + y = 0 , y(\ln 4) = \frac{1}{5}")
    result = solver.solve(parsed)

    assert result is not None
    assert "2" in result.answer and "5" in result.answer and "e" in result.answer


def test_differential_linear_cauchy_4_ko():
    r"""Exercise 4.គ: 7y' + 4y = 0, y(7) = e^{-4} -> y = e^{-(4/7)x}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"7y' + 4y = 0 , y(7) = e^{-4}")
    result = solver.solve(parsed)

    assert result is not None
    assert "e" in result.answer and "7" in result.answer


def test_differential_linear_cauchy_4_kho():
    r"""Exercise 4.ឃ: 2y' - 5y = 0, y(1) = -3 -> y = -3 e^{(5/2)(x - 1)}."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"2y' - 5y = 0 , y(1) = -3")
    result = solver.solve(parsed)

    assert result is not None
    assert "- 3" in result.answer or "-3" in result.answer


# ==============================================================================
# Exercise 5: Verification of Solutions
# ==============================================================================

def test_differential_verification_5_ka():
    r"""Exercise 5.ក: y = x + e^x is solution of y' - y = 1 - x."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y = x + e^x , y' - y = 1 - x")
    assert parsed.metadata.get("is_verification") is True

    result = solver.solve_verification(
        parsed.metadata["function_rhs"],
        parsed.metadata["differential_eq"],
    )
    assert result.is_verified is True
    assert "ពិត" in result.answer
    assert len(result.steps) >= 3


def test_differential_verification_5_kha():
    r"""Exercise 5.ខ: y = e^{3x} - x - 1 is solution of y' - 3y = 3x + 2."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y = e^{3x} - x - 1 , y' - 3y = 3x + 2")
    assert parsed.metadata.get("is_verification") is True

    result = solver.solve_verification(
        parsed.metadata["function_rhs"],
        parsed.metadata["differential_eq"],
    )
    assert result.is_verified is True
    assert "ពិត" in result.answer


def test_differential_verification_5_ko():
    r"""Exercise 5.គ: y = \sin x + \cos x is solution of y' + y = 2\cos x."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"y = \sin x + \cos x , y' + y = 2\cos x")
    assert parsed.metadata.get("is_verification") is True

    result = solver.solve_verification(
        parsed.metadata["function_rhs"],
        parsed.metadata["differential_eq"],
    )
    assert result.is_verified is True
    assert "ពិត" in result.answer


# ==============================================================================
# End-to-End: process_question pipeline
# ==============================================================================

def test_process_question_differential_direct():
    """Test process_question for a differential equation."""
    res = process_question(r"ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល y' = 2x^2 - x + 1")
    assert res.problem_type == "calculus_differential_equation"
    assert res.answer is not None
    assert "x^{3}" in res.answer or "x^3" in res.answer
    assert "3" in res.answer


def test_process_question_differential_cauchy():
    """Test process_question for linear homogeneous ODE with initial condition."""
    res = process_question(r"ដោះស្រាយសមីការ y' + 2y = 0 , y(0) = 3")
    assert res.problem_type == "calculus_differential_equation"
    assert res.answer is not None
    assert "3" in res.answer
    assert "e" in res.answer


def test_differential_verification_second_order():
    """Verify f(x) = (2x+1)e^{-x} satisfies y'' + 2y' + y = 0."""
    solver = get_solver("calculus_differential_equation")
    assert solver is not None

    parsed = parse_math_text(r"f(x) = (2x+1)e^{-x} , y'' + 2y' + y = 0")
    assert parsed.metadata.get("is_verification") is True

    result = solver.solve_verification(
        parsed.metadata["function_rhs"],
        parsed.metadata["differential_eq"],
    )
    assert result.is_verified is True
    assert "ពិត" in result.answer


def test_process_question_user_ocr_differential_verification():
    """Test full pipeline on user exact OCR detected string."""
    q = (
        r"1. ធ្ទៀងផ្ទាត់ថាអនុគមន៍ / ជាចម្លើយនៃសមីការឌីផេរំង័ពស្បួលដែលគេឱ្យនៅខាងស្ដាំ : "
        r"ក. f(x) = (2x+1)e^{-x} , y^{\prime\prime}+2y^{\prime}+y = 0"
    )
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert res.is_verified is True
    assert "ពិត" in res.answer
    assert len(res.steps) == 3
    # Check steps have Khmer pedagogical explanations
    assert any("ដេរីវេទី១" in s.description_km for s in res.steps)
    assert any("ដេរីវេទី២" in s.description_km for s in res.steps)


def test_process_question_user_image_problem_ko():
    """Test f(x) = Ae^x + Bxe^x , y'' - 2y' + y = 0 with arbitrary constants A and B."""
    q = "គ. f(x) = Ae^x + Bxe^x , y'' - 2y' + y = 0 ដែល A និង B ជាចំនួនថេរណាមួយក៏បាន ។"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert res.is_verified is True
    assert "ពិត" in res.answer
    assert len(res.steps) == 3


# ==============================================================================
# Second Form (ទម្រង់ទី២) Tests: Grade 12 BacII Chapter 6
# ==============================================================================

def test_form_ode_image6_ka():
    """Exercise 3.ក from image6.png: f(x) = (x+1)e^{-2x} -> y'' + 4y' + 4y = 0."""
    q = "រកសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទីពីរ អូម៉ូសែនដែលមានអនុគមន៍ f ជាចម្លើយ: f(x) = (x + 1)e^{-2x}"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "y'' + 4y' + 4y = 0" in res.answer
    assert len(res.steps) == 4
    assert any("ដេរីវេទីមួយ និងទីពីរ" in s.title_km for s in res.steps)
    assert any("មេគុណ a និង b" in s.title_km for s in res.steps)


def test_form_ode_image6_kha():
    """Exercise 3.ខ from image6.png: f(x) = 2e^{-x} + 3e^{3x} -> y'' - 2y' - 3y = 0."""
    q = "រកសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទីពីរ អូម៉ូសែនដែលមានអនុគមន៍ f ជាចម្លើយ: f(x) = 2e^{-x} + 3e^{3x}"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "y'' - 2y' - 3y = 0" in res.answer
    assert len(res.steps) == 4


def test_form_ode_image6_ko():
    r"""Exercise 3.គ from image6.png: f(x) = (2\cos 3x - 3\sin 3x)e^x -> y'' - 2y' + 10y = 0."""
    q = r"រកសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទីពីរ អូម៉ូសែនដែលមានអនុគមន៍ f ជាចម្លើយ: f(x) = (2\cos 3x - 3\sin 3x)e^x"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "y'' - 2y' + 10y = 0" in res.answer
    assert len(res.steps) == 4


def test_second_order_ode_double_root():
    """Solve y'' + 4y' + 4y = 0 (Delta = 0)."""
    q = "y'' + 4y' + 4y = 0"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "(C_1 x + C_2)" in res.answer or "(C_1x + C_2)" in res.answer
    assert "e^{- 2 x}" in res.answer or "e^{-2x}" in res.answer
    assert len(res.steps) == 3
    assert any("សមីការសម្គាល់" in s.title_km for s in res.steps)


def test_second_order_ode_distinct_roots():
    """Solve y'' - 2y' - 3y = 0 (Delta > 0)."""
    q = "y'' - 2y' - 3y = 0"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "e^{3 x}" in res.answer or "e^{3x}" in res.answer
    assert "e^{- x}" in res.answer or "e^{-x}" in res.answer
    assert len(res.steps) == 3


def test_second_order_ode_complex_roots():
    """Solve y'' - 2y' + 10y = 0 (Delta < 0)."""
    q = "y'' - 2y' + 10y = 0"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "cos" in res.answer and "sin" in res.answer
    assert "e^{x}" in res.answer or "e^x" in res.answer
    assert len(res.steps) == 3


def test_second_order_ode_cauchy_initial_conditions():
    """Solve y'' - 2y' - 3y = 0 with y(0) = 5, y'(0) = 7 -> y = 3e^{3x} + 2e^{-x}."""
    q = "y'' - 2y' - 3y = 0 , y(0) = 5 , y'(0) = 7"
    res = process_question(q)
    assert res.problem_type == "calculus_differential_equation"
    assert "3 e^{3 x} + 2 e^{- x}" in res.answer or "2 e^{- x} + 3 e^{3 x}" in res.answer
    assert len(res.steps) == 5

