"""
Tests for calculus derivative solver, lesson-aware step generation, and Khmer BacII curriculum alignment.
"""

from __future__ import annotations

import pytest
import sympy
from sympy import Symbol

from app.classifier.context_aware_classifier import ContextAwareClassifier
from app.models.document import Instruction, InstructionType
from app.parser.exercise_parser.exercise_parser import parse_exercise
from app.parser.instruction_parser.instruction_detector import InstructionDetector
from app.parser.math_parser.expression_parser import parse_math_text
from app.reasoning.steps.registry import get_step_generator
from app.solvers.registry import get_solver


def test_derivative_solver_radical_chain():
    r"""Test image.png: y = \sqrt{x^2 - 1} -> y' = x / \sqrt{x^2 - 1}."""
    parsed = parse_math_text(r"y = \sqrt{x^2 - 1}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check pedagogical steps
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តប្រមាណវិធីដេរីវេ" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃកន្សោមខាងក្នុង" in result.steps[2].title_km
    assert "សម្រួលកន្សោម" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_radical_chain"
    assert "ជំពូកទី៣" in result.lesson_info["chapter_km"]


def test_derivative_solver_exponential_quotient_explain():
    """Test image1.png + explain.png: f(x) = e^x + 3 - e^x/(e^x + 3)."""
    parsed = parse_math_text(r"f(x) = e^x + 3 - \frac{e^x}{e^x + 3}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness against ground truth explain.png
    x = Symbol("x")
    expected = (sympy.exp(2 * x) + 6 * sympy.exp(x) + 6) * sympy.exp(x) / (sympy.exp(x) + 3) ** 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"
    assert "វិធានដេរីវេអិចស្បូណង់ស្យែល" in result.lesson_info["method_km"]


def test_derivative_solver_reciprocal_power():
    """Test telegram photo: y = 1 / (x^2 + 3x + 1)^2 -> y' = -2(2x + 3)/(x^2 + 3x + 1)^3."""
    parsed = parse_math_text(r"y = \frac{1}{(x^2 + 3x + 1)^2}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = -2 * (2 * x + 3) / (x**2 + 3 * x + 1) ** 3
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_reciprocal_power"
    assert "វិធានដេរីវេចម្រាសស្វ័យគុណ" in result.lesson_info["method_km"]


def test_end_to_end_telegram_exercise_pipeline():
    """Test full parsing and context classification on Telegram exercise text."""
    raw_text = r"គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម ៈ ឃ. y = \frac{1}{(x^2 + 3x + 1)^2}"
    parsed_ex = parse_exercise(raw_text)
    assert parsed_ex.instruction is not None
    assert "គណនាដេរីវេ" in parsed_ex.instruction

    det = InstructionDetector()
    inst = det.detect(parsed_ex.instruction)
    assert inst is not None
    assert inst.action.value == "derive"

    inst_model = inst.to_instruction()
    assert inst_model.instruction_type == InstructionType.DERIVATIVE

    parsed_math = parse_math_text(parsed_ex.primary_expression)
    cac = ContextAwareClassifier()
    c_res = cac.classify(parsed_math, instruction=inst_model)
    assert c_res.problem_type == "calculus_derivative"

    solver = get_solver(c_res.problem_type)
    sol = solver.solve(parsed_math, c_res.problem_type)
    assert sol.answer is not None
    assert len(sol.steps) == 5


def test_function_definition_classified_as_derivative():
    """Test f(x) = ... is recognized as calculus_derivative."""
    parsed = parse_math_text(r"f(x) = x^3 - 3x + 2")
    cac = ContextAwareClassifier()
    c_res = cac.classify(parsed)
    assert c_res.problem_type == "calculus_derivative"

    solver = get_solver("calculus_derivative")
    sol = solver.solve(parsed, "calculus_derivative")
    assert sol.answer == "3*(x - 1)*(x + 1)" or sol.answer == "3*x**2 - 3"


def test_derivative_solver_image2_quotient_log():
    r"""Test image2.png: f(x) = \frac{x\ln x}{x+1} -> f'(x) = \frac{x + \ln x + 1}{(x+1)^2}."""
    parsed = parse_math_text(r"f(x) = \frac{x \ln x}{x + 1}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = (x + sympy.log(x) + 1) / (x + 1) ** 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: quotient rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_quotient_rule"
    assert "ផលចែក" in result.lesson_info["method_km"]

    # Pedagogical steps in Khmer BacII format
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តវិធានផលចែក" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃភាគយក និងភាគបែង" in result.steps[2].title_km
    assert "ពង្រាយ និងសម្រួលភាគយក" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km

    # Verify \ln is used instead of \log in student steps
    for step in result.steps:
        assert r"\log" not in step.expression
        assert r"\log" not in step.description_km


def test_derivative_solver_image3_sub_k_product_exp():
    r"""Test image3.png sub-exercise ក: y = x e^{-x} -> y' = -(x - 1)e^{-x}."""
    parsed = parse_math_text(r"y = x e^{-x}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = -(x - 1) * sympy.exp(-x)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: exponential rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"
    assert "អិចស្បូណង់ស្យែល" in result.lesson_info["method_km"]

    # Pedagogical steps in Khmer BacII format
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តវិធានផលគុណ" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃកត្តានីមួយៗ" in result.steps[2].title_km
    assert "ដាក់ជាផលគុណកត្តា" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km


def test_derivative_solver_image3_sub_kh_product_exp():
    r"""Test image3.png sub-exercise ខ: f(x) = x^2 e^x -> f'(x) = x(x + 2)e^x."""
    parsed = parse_math_text(r"f(x) = x^2 e^x")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = x * (x + 2) * sympy.exp(x)
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: exponential rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"
    assert "អិចស្បូណង់ស្យែល" in result.lesson_info["method_km"]

    # Pedagogical steps in Khmer BacII format
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តវិធានផលគុណ" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃកត្តានីមួយៗ" in result.steps[2].title_km
    assert "ដាក់ជាផលគុណកត្តា" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km


def test_derivative_solver_image4_sub_k_hyperbolic_exp():
    r"""Test image4.png sub-exercise ក: y = \frac{e^x + e^{-x}}{2} -> y' = \frac{e^x - e^{-x}}{2}."""
    parsed = parse_math_text(r"y = \frac{e^x + e^{-x}}{2}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = (sympy.exp(x) - sympy.exp(-x)) / 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: exponential rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"
    assert "អិចស្បូណង់ស្យែល" in result.lesson_info["method_km"]

    # Pedagogical steps in Khmer BacII format
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តប្រមាណវិធីដេរីវេ" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃភាគយក" in result.steps[2].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km


def test_derivative_solver_image4_sub_kh_quotient_trig_exp():
    r"""Test image4.png sub-exercise ខ: f(x) = \frac{e^x(1 + \cos x)}{1 - \cos x} -> f'(x) = \frac{e^x \sin x (\sin x - 2)}{(1 - \cos x)^2}."""
    parsed = parse_math_text(r"f(x) = \frac{e^x(1 + \cos x)}{1 - \cos x}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = sympy.exp(x) * sympy.sin(x) * (sympy.sin(x) - 2) / (1 - sympy.cos(x)) ** 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: exponential rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"

    # Pedagogical steps in Khmer BacII format (quotient rule)
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តវិធានផលចែក" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃភាគយក និងភាគបែង" in result.steps[2].title_km
    assert "ពង្រាយ និងសម្រួលភាគយក" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km


@pytest.mark.parametrize(
    "label,latex,expected_expr",
    [
        (
            "ក",
            r"f(x) = e^x + 3 - \frac{e^x}{e^x + 3}",
            sympy.exp(Symbol("x"))
            * (sympy.exp(2 * Symbol("x")) + 6 * sympy.exp(Symbol("x")) + 6)
            / (sympy.exp(Symbol("x")) + 3) ** 2,
        ),
        (
            "ខ",
            r"f(x) = \frac{x \ln x}{x + 1}",
            (Symbol("x") + sympy.log(Symbol("x")) + 1) / (Symbol("x") + 1) ** 2,
        ),
        (
            "គ",
            r"f(x) = \frac{x^2 \ln x}{x - 1}",
            (
                Symbol("x") ** 2 * sympy.log(Symbol("x"))
                - 2 * Symbol("x") * sympy.log(Symbol("x"))
                + Symbol("x") ** 2
                - Symbol("x")
            )
            / (Symbol("x") - 1) ** 2,
        ),
        (
            "ឃ",
            r"g(x) = (x - 2)\ln(x) + x - 1",
            (Symbol("x") * sympy.log(Symbol("x")) + 2 * Symbol("x") - 2) / Symbol("x"),
        ),
        (
            "ង",
            r"f(x) = x e^{1 - x}",
            (1 - Symbol("x")) * sympy.exp(1 - Symbol("x")),
        ),
        (
            "ច",
            r"h(x) = 1 + \frac{1}{x^2} - 2\ln(x)",
            -2 * (Symbol("x") ** 2 + 1) / Symbol("x") ** 3,
        ),
        (
            "ឆ",
            r"g(x) = x^2 (1 - \ln(x)) + 1 + \ln(x)",
            (Symbol("x") ** 2 - 2 * Symbol("x") ** 2 * sympy.log(Symbol("x")) + 1) / Symbol("x"),
        ),
        (
            "ជ",
            r"f(x) = \frac{x \ln(x)}{1 + x^2}",
            (
                -Symbol("x") ** 2 * sympy.log(Symbol("x"))
                + sympy.log(Symbol("x"))
                + Symbol("x") ** 2
                + 1
            )
            / (1 + Symbol("x") ** 2) ** 2,
        ),
        (
            "ឈ",
            r"f(x) = (4 - x) e^{\frac{1}{2}x}",
            (2 - Symbol("x")) * sympy.exp(Symbol("x") / 2) / 2,
        ),
        (
            "ញ",
            r"g(x) = \frac{1}{4} e^{2x} (\cos(2x) + \sin(2x))",
            sympy.exp(2 * Symbol("x")) * sympy.cos(2 * Symbol("x")),
        ),
        (
            "ដ",
            r"h(x) = \frac{2e^x + 2x - 2}{e^x}",
            (4 - 2 * Symbol("x")) / sympy.exp(Symbol("x")),
        ),
        (
            "ឋ",
            r"f(x) = x - \frac{e^x - 1}{e^x + 1}",
            (sympy.exp(2 * Symbol("x")) + 1) / (sympy.exp(Symbol("x")) + 1) ** 2,
        ),
        (
            "ឌ",
            r"g(x) = 1 + \ln\left(2 + \frac{1}{x}\right)",
            -1 / (Symbol("x") * (2 * Symbol("x") + 1)),
        ),
        (
            "ឍ",
            r"h(x) = \frac{-2x}{x + 2} + \ln(x + 1)",
            Symbol("x") ** 2 / ((Symbol("x") + 1) * (Symbol("x") + 2) ** 2),
        ),
    ],
)
def test_derivative_pdf_all_14_worksheet_exercises(label, latex, expected_expr):
    """Test all 14 exercises from BacII homework PDF 642f657a-7cd5-44b6-bf59-f14d680beb09.pdf."""
    parsed = parse_math_text(latex)
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected_expr) == 0

    # Ensure 5-step pedagogical structure
    assert result.steps[0].title_km == "កំណត់អនុគមន៍ដើម"
    assert "ដេរីវេ" in result.steps[1].title_km or "ផល" in result.steps[1].title_km
    assert result.steps[4].title_km == "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ"




