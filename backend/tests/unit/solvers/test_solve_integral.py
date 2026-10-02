"""
Unit and integration tests for Cambodian Grade 12 BacII Chapter 5:
អាំងតេក្រាល (Calculus Integrals & Primitives).

Covers exercises from:
- training/test_exercises/integrals/image.png
- training/test_exercises/integrals/image1.png
Includes:
- Exercise 1: Verification of primitives F'(x) = f(x)
- Exercise 3 & 4: Initial value problems / particular antiderivatives
- Exercise 5: Indefinite integrals (Power, Rational, Radical, Trig, Exp)
- Exercise 6: Composite exponential integration ∫ u' eᵘ dx = eᵘ + C
- Exercise 7: Integration by parts ∫ u dv = uv - ∫ v du
- Definite integrals & API endpoints
"""

from __future__ import annotations

import pytest
import sympy
from fastapi.testclient import TestClient
from sympy import Rational, Symbol, cos, exp, log, pi, sin, sqrt

from app.main import app
from app.parser.math_parser.expression_parser import parse_math_text
from app.services.math_service import process_question
from app.solvers.registry import get_solver


@pytest.fixture
def client():
    return TestClient(app)


# ==============================================================================
# Exercise 1: Verification of Primitives (F'(x) = f(x))
# ==============================================================================

def test_primitive_verification_1_ka():
    r"""Exercise 1.ក: F(x) = -7x + 4, f(x) = -7."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_verification(-7 * x + 4, -7, x)
    assert result.is_verified is True
    assert result.answer == "ពិត"
    assert len(result.steps) == 4
    assert result.lesson_info["method_id"] == "method_primitive_verification"


def test_primitive_verification_1_kha():
    r"""Exercise 1.ខ: F(x) = 3x^3 - 7x, f(x) = 9x^2 - 7."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_verification(3 * x**3 - 7 * x, 9 * x**2 - 7, x)
    assert result.is_verified is True
    assert result.answer == "ពិត"
    assert len(result.steps) == 4


def test_primitive_verification_1_ko():
    r"""Exercise 1.គ: F(x) = 3e^{x^2 - 1} - 7, f(x) = 6x e^{x^2 - 1}."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    F = 3 * exp(x**2 - 1) - 7
    f = 6 * x * exp(x**2 - 1)
    result = solver.solve_verification(F, f, x)
    assert result.is_verified is True
    assert result.answer == "ពិត"


def test_primitive_verification_1_kho():
    r"""Exercise 1.ឃ: F(x) = \ln(e^{3x} - x) + \sqrt{11}, f(x) = \frac{3e^{3x} - 1}{e^{3x} - x}."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    F = log(exp(3 * x) - x) + sqrt(11)
    f = (3 * exp(3 * x) - 1) / (exp(3 * x) - x)
    result = solver.solve_verification(F, f, x)
    assert result.is_verified is True
    assert result.answer == "ពិត"


# ==============================================================================
# Exercise 3 & 4: Particular Antiderivatives with Initial Conditions
# ==============================================================================

def test_primitive_initial_value_3_kha():
    r"""Exercise 3.ខ: f(x) = x^2 - x, F(0) = 1 -> F(x) = x^3/3 - x^2/2 + 1."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_initial_value(x**2 - x, x, 0, 1)
    expected = x**3 / 3 - x**2 / 2 + 1
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0
    assert len(result.steps) == 4
    assert result.lesson_info["method_id"] == "method_primitive_initial_value"


def test_primitive_initial_value_3_ko():
    r"""Exercise 3.គ: f(x) = x^2 - e^x, F(0) = 1 -> F(x) = x^3/3 - e^x + 2."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_initial_value(x**2 - exp(x), x, 0, 1)
    expected = x**3 / 3 - exp(x) + 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0


def test_primitive_initial_value_4_ka():
    r"""Exercise 4.ក: f(x) = \sin x, F(0) = 3 -> F(x) = -\cos x + 4."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_initial_value(sin(x), x, 0, 3)
    expected = -cos(x) + 4
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0


def test_primitive_initial_value_4_kha():
    r"""Exercise 4.ខ: f(x) = x - e^x, F(1) = 1 - e -> F(x) = x^2/2 - e^x + 1/2."""
    solver = get_solver("calculus_integral")
    assert solver is not None
    x = Symbol("x")

    result = solver.solve_initial_value(x - exp(x), x, 1, 1 - exp(1))
    expected = x**2 / 2 - exp(x) + Rational(1, 2)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0


# ==============================================================================
# Exercise 5: Indefinite Integrals (Polynomial, Rational, Trig, Exp)
# ==============================================================================

def test_integral_exercise_5_sub_ka():
    r"""Exercise 5.ក: \int (2x^3 - 5x^2 + 3x + 1) dx."""
    parsed = parse_math_text(r"\int (2x^3 - 5x^2 + 3x + 1) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    assert result.answer is not None
    assert "+ C" in result.answer
    assert result.lesson_info["method_id"] == "method_integral_power_rule"
    assert len(result.steps) >= 4


def test_integral_exercise_5_sub_kha():
    r"""Exercise 5.ខ: \int (5 - \frac{1}{\sqrt{x}}) dx -> 5x - 2\sqrt{x} + C."""
    parsed = parse_math_text(r"\int (5 - \frac{1}{\sqrt{x}}) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = 5 * x - 2 * sqrt(x)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_5_sub_chhor():
    r"""Exercise 5.ឈ: \int (3\sin x + 5\cos x) dx -> -3\cos x + 5\sin x + C."""
    parsed = parse_math_text(r"\int (3\sin x + 5\cos x) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = 5 * sin(x) - 3 * cos(x)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_trigonometric"


def test_integral_exercise_5_sub_da():
    r"""Exercise 5.ដ: \int \frac{e^{3x} + 1}{e^x + 1} dx -> e^{2x}/2 - e^x + x + C."""
    parsed = parse_math_text(r"\int \frac{e^{3x} + 1}{e^x + 1} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = exp(2 * x) / 2 - exp(x) + x
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


# ==============================================================================
# Exercise 6: Composite Exponential Integration (∫ u' eᵘ dx = eᵘ + C)
# ==============================================================================

def test_integral_exercise_6_sub_ka():
    r"""Exercise 6.ក: \int 3e^{3x} dx -> e^{3x} + C."""
    parsed = parse_math_text(r"\int 3e^{3x} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - exp(3 * x)) == 0


def test_integral_exercise_6_sub_kha():
    r"""Exercise 6.ខ: \int 2x e^{x^2} dx -> e^{x^2} + C."""
    parsed = parse_math_text(r"\int 2x e^{x^2} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - exp(x**2)) == 0
    assert result.lesson_info["method_id"] == "method_integral_exp_composite"
    assert len(result.steps) == 4


def test_integral_exercise_6_sub_kho():
    r"""Exercise 6.ឃ: \int (6x - 7)e^{3x^2 - 7x} dx -> e^{3x^2 - 7x} + C."""
    parsed = parse_math_text(r"\int (6x - 7)e^{3x^2 - 7x} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - exp(3 * x**2 - 7 * x)) == 0
    assert result.lesson_info["method_id"] == "method_integral_exp_composite"


# ==============================================================================
# Exercise 7: Integration by Parts (∫ u dv = uv - ∫ v du)
# ==============================================================================

def test_integral_exercise_7_sub_ka_exp_by_parts():
    r"""Exercise 7.ក: \int x e^{-x} dx -> -(x + 1)e^{-x} + C."""
    parsed = parse_math_text(r"\int x e^{-x} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = -(x + 1) * exp(-x)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"
    assert len(result.steps) == 5

    # Check that Step 2 contains u and dv derivation
    assert "u =" in result.steps[1].expression
    assert "dv =" in result.steps[1].expression


def test_integral_exercise_7_sub_tho_log_by_parts():
    r"""Exercise 7.ធ: \int x^2 \ln x dx -> x^3 \ln(x)/3 - x^3/9 + C."""
    parsed = parse_math_text(r"\int x^2 \ln x \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = x**3 * log(x) / 3 - x**3 / 9
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"
    assert len(result.steps) == 5


def test_integral_exercise_7_sub_bo_rational_log_by_parts():
    r"""Exercise 7.ប: \int \frac{\ln x}{x^2} dx -> -\frac{\ln x}{x} - \frac{1}{x} + C."""
    parsed = parse_math_text(r"\int \frac{\ln x}{x^2} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = -log(x) / x - 1 / x
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"


def test_integral_exercise_5_sub_ko():
    r"""Exercise 5.គ: \int (\frac{x^2}{2} - \frac{2}{x^2}) dx -> x^3/6 + 2/x + C."""
    parsed = parse_math_text(r"\int \left(\frac{x^2}{2} - \frac{2}{x^2}\right) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = x**3 / 6 + 2 / x
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_5_sub_kho():
    r"""Exercise 5.ឃ: \int (\sqrt{x} + \frac{1}{2\sqrt{x}}) dx -> 2x^{3/2}/3 + \sqrt{x} + C."""
    parsed = parse_math_text(r"\int \left(\sqrt{x} + \frac{1}{2\sqrt{x}}\right) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = Rational(2, 3) * x ** Rational(3, 2) + sqrt(x)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_5_sub_jhor():
    r"""Exercise 5.ជ: \int (2x - 3)^2 dx -> 4x^3/3 - 6x^2 + 9x + C."""
    parsed = parse_math_text(r"\int (2x - 3)^2 \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = Rational(4, 3) * x**3 - 6 * x**2 + 9 * x
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_5_sub_nhor():
    r"""Exercise 5.ញ: \int (1 - e^x)^2 dx -> x - 2e^x + e^{2x}/2 + C."""
    parsed = parse_math_text(r"\int (1 - e^x)^2 \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = x - 2 * exp(x) + exp(2 * x) / 2
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_6_sub_ko():
    r"""Exercise 6.គ: \int (2x-1) e^{x^2-x+3} dx -> e^{x^2-x+3} + C."""
    parsed = parse_math_text(r"\int (2x - 1) e^{x^2 - x + 3} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = exp(x**2 - x + 3)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_exp_composite"


def test_integral_exercise_6_sub_chha():
    r"""Exercise 6.ច: \int \frac{e^{\sqrt{x}}}{\sqrt{x}} dx -> 2 e^{\sqrt{x}} + C."""
    parsed = parse_math_text(r"\int \frac{e^{\sqrt{x}}}{\sqrt{x}} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = 2 * exp(sqrt(x))
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_exp_composite"


def test_integral_exercise_6_sub_chhor_trig():
    r"""Exercise 6.ឈ: \int \cos x \, e^{\sin x} dx -> e^{\sin x} + C."""
    parsed = parse_math_text(r"\int \cos x \, e^{\sin x} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = exp(sin(x))
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_exp_composite"


def test_integral_exercise_6_sub_da_exp_sum():
    r"""Exercise 6.ដ: \int (e^x + e^{-x})^2 dx -> e^{2x}/2 + 2x - e^{-2x}/2 + C."""
    parsed = parse_math_text(r"\int (e^x + e^{-x})^2 \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = exp(2 * x) / 2 + 2 * x - exp(-2 * x) / 2
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0


def test_integral_exercise_7_sub_kha():
    r"""Exercise 7.ខ: \int x e^{2x} dx -> (2x - 1)e^{2x}/4 + C."""
    parsed = parse_math_text(r"\int x e^{2x} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = (2 * x - 1) * exp(2 * x) / 4
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"


def test_integral_exercise_7_sub_chhor_radical():
    r"""Exercise 7.ឈ: \int x \sqrt{x-6} dx -> 2(x+4)(x-6)^{3/2}/5 + C."""
    parsed = parse_math_text(r"\int x \sqrt{x - 6} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = Rational(2, 5) * (x + 4) * (x - 6) ** Rational(3, 2)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"


def test_integral_exercise_7_sub_nhor_quotient():
    r"""Exercise 7.ញ: \int \frac{x}{\sqrt{x+2}} dx -> 2(x-4)\sqrt{x+2}/3 + C."""
    parsed = parse_math_text(r"\int \frac{x}{\sqrt{x + 2}} \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = Rational(2, 3) * (x - 4) * sqrt(x + 2)
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"


def test_integral_exercise_7_sub_da_power():
    r"""Exercise 7.ដ: \int x (x + 1)^8 dx -> (x+1)^9(9x - 1)/90 + C."""
    parsed = parse_math_text(r"\int x (x + 1)^8 \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    x = Symbol("x")
    expected = (x + 1) ** 9 * (9 * x - 1) / 90
    ans_clean = result.answer.replace("+ C", "").strip()
    assert sympy.simplify(sympy.sympify(ans_clean) - expected) == 0
    assert result.lesson_info["method_id"] == "method_integral_by_parts"


# ==============================================================================
# Definite Integrals & API Integration Tests
# ==============================================================================

def test_integral_definite_polynomial():
    r"""Test definite integral: \int_0^1 x^2 dx = 1/3."""
    parsed = parse_math_text(r"\int_0^1 x^2 \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    assert result.answer == "1/3"
    assert len(result.steps) == 5
    assert result.lesson_info["method_id"] == "method_integral_definite"


def test_integral_image3_exercise_a():
    r"""Image 3: A = \int_2^4 (x^2 + 2/x^3 + \sqrt{x} - 3) dx = 291/16 - 4\sqrt{2}/3."""
    parsed = parse_math_text(r"A = \int_2^4 \left(x^2 + \frac{2}{x^3} + \sqrt{x} - 3\right) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    expected = Rational(291, 16) - 4 * sqrt(2) / 3
    assert sympy.simplify(sympy.sympify(result.answer) - expected) == 0
    assert len(result.steps) == 5
    assert result.lesson_info["method_id"] == "method_integral_definite"


def test_integral_image2_exercise_b():
    r"""Image 2: B = \int_{\pi/2}^\pi (\sin\frac{x}{2} + 4x - 1) dx = 3\pi^2/2 - \pi/2 + \sqrt{2}."""
    parsed = parse_math_text(r"B = \int_{\pi/2}^\pi \left(\sin\frac{x}{2} + 4x - 1\right) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None

    result = solver.solve(parsed, "calculus_integral")
    expected = 3 * pi**2 / 2 - pi / 2 + sqrt(2)
    assert sympy.simplify(sympy.sympify(result.answer) - expected) == 0
    assert len(result.steps) == 5
    assert result.lesson_info["method_id"] == "method_integral_definite"


def test_integral_definite_polynomial_evaluation():
    r"""Definite: \int_1^2 (3x^2 - 2x + 1) dx = 5."""
    parsed = parse_math_text(r"\int_1^2 (3x^2 - 2x + 1) \, dx")
    solver = get_solver("calculus_integral")
    assert solver is not None
    result = solver.solve(parsed, "calculus_integral")
    assert sympy.simplify(sympy.sympify(result.answer) - 5) == 0


def test_integral_definite_trigonometric():
    r"""Definite: \int_0^{\pi/2} \cos x dx = 1 and \int_0^{\pi/4} 1/\cos^2 x dx = 1."""
    solver = get_solver("calculus_integral")
    assert solver is not None

    p1 = parse_math_text(r"\int_0^{\pi/2} \cos x \, dx")
    r1 = solver.solve(p1, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r1.answer) - 1) == 0

    p2 = parse_math_text(r"\int_0^{\pi/4} \frac{1}{\cos^2 x} \, dx")
    r2 = solver.solve(p2, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r2.answer) - 1) == 0


def test_integral_definite_exponential():
    r"""Definite: \int_0^1 e^{2x} dx = (e^2-1)/2 and \int_0^1 2x e^{x^2} dx = e - 1."""
    solver = get_solver("calculus_integral")
    assert solver is not None

    p1 = parse_math_text(r"\int_0^1 e^{2x} \, dx")
    r1 = solver.solve(p1, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r1.answer) - (exp(2) - 1) / 2) == 0

    p2 = parse_math_text(r"\int_0^1 2x e^{x^2} \, dx")
    r2 = solver.solve(p2, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r2.answer) - (exp(1) - 1)) == 0


def test_integral_definite_logarithmic_rational():
    r"""Definite: \int_1^e 1/x dx = 1 and \int_1^e \frac{\ln x}{x} dx = 1/2."""
    solver = get_solver("calculus_integral")
    assert solver is not None

    p1 = parse_math_text(r"\int_1^e \frac{1}{x} \, dx")
    r1 = solver.solve(p1, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r1.answer) - 1) == 0

    p2 = parse_math_text(r"\int_1^e \frac{\ln x}{x} \, dx")
    r2 = solver.solve(p2, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r2.answer) - Rational(1, 2)) == 0


def test_integral_definite_by_parts():
    r"""Definite: \int_0^1 x e^x dx = 1 and \int_1^e x \ln x dx = (e^2+1)/4."""
    solver = get_solver("calculus_integral")
    assert solver is not None

    p1 = parse_math_text(r"\int_0^1 x e^x \, dx")
    r1 = solver.solve(p1, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r1.answer) - 1) == 0

    p2 = parse_math_text(r"\int_1^e x \ln x \, dx")
    r2 = solver.solve(p2, "calculus_integral")
    assert sympy.simplify(sympy.sympify(r2.answer) - (exp(2) + 1) / 4) == 0


def test_integral_e2e_process_question():
    r"""Test process_question with Khmer instruction: គណនាអាំងតេក្រាល \int x e^{-x} dx."""
    res = process_question(r"គណនាអាំងតេក្រាល \int x e^{-x} dx")
    assert res.problem_type == "calculus_integral"
    assert res.lesson_info is not None
    assert "មេរៀនទី១ : ព្រីមីទីវ និងអាំងតេក្រាលមិនកំណត់" in res.lesson_info["lesson_km"]
    assert res.lesson_info["method_id"] == "method_integral_by_parts"


def test_integral_api_solve_endpoint(client):
    r"""Test POST /api/v1/math/solve with integral."""
    resp = client.post("/api/v1/math/solve", json={"question": r"\int 2x e^{x^2} dx"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "exp(x**2) + C" in data["answer"]
    assert data["problem_type"] == "calculus_integral"
    assert data["lesson_info"]["method_id"] == "method_integral_exp_composite"
