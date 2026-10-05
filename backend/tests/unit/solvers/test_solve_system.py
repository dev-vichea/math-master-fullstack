"""
Unit tests for system of equations solver and Tuple classification.
"""

import pytest
import sympy
from sympy import Eq, Symbol

from app.classifier.problem_classifier.classifier import classify_problem
from app.parser.math_parser.expression_parser import ParsedMath, parse_math_text
from app.services.math_service import process_question
from app.solvers.algebra.system_solver import SystemSolver


def test_classify_tuple_equations():
    """Verify that a Tuple of equations never raises AttributeError for .lhs."""
    x = Symbol("x")
    y = Symbol("y")
    composite_tuple = sympy.Tuple(Eq(2 * x + y, 5), Eq(x - y, 1))

    parsed = ParsedMath(
        raw_text="2x + y = 5, x - y = 1",
        is_equation=True,
        sympy_expr=composite_tuple,
        symbols=[x, y],
    )

    problem_type = classify_problem(parsed)
    assert problem_type == "system_linear_2x2"


def test_solve_system_2x2_comma_separated():
    res = process_question("2x + y = 5, x - y = 1")
    assert res.problem_type == "system_linear_2x2"
    assert "x = 2" in res.answer
    assert "y = 1" in res.answer
    assert len(res.steps) >= 3


def test_solve_system_2x2_cases_latex():
    raw = r"\begin{cases} 2x + y = 5 \\ x - y = 1 \end{cases}"
    res = process_question(raw)
    assert res.problem_type == "system_linear_2x2"
    assert "x = 2" in res.answer
    assert "y = 1" in res.answer
    assert len(res.steps) >= 3


def test_solve_system_3x3_cases_latex():
    raw = r"\begin{cases} x + y + z = 6 \\ 2x - y + z = 3 \\ x + 2y - z = 2 \end{cases}"
    res = process_question(raw)
    assert res.problem_type == "system_linear_3x3"
    assert "x = 1" in res.answer
    assert "y = 2" in res.answer
    assert "z = 3" in res.answer
    assert len(res.steps) >= 3


def test_solve_system_inconsistent():
    raw = "x + y = 1, x + y = 2"
    res = process_question(raw)
    assert res.problem_type == "system_linear_2x2"
    assert "គ្មានចម្លើយ" in res.answer or "No solution" in res.answer
