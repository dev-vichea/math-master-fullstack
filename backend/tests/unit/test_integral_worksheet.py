"""Unit tests for integral OCR repair, parsing, and worksheet integration."""

import pytest
from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text
from app.parser.math_parser.expression_parser import parse_math_text
from app.classifier.problem_classifier.classifier import classify_problem
from app.solvers import solve
from app.services.exercise_service import ExerciseService
from app.services.worksheet_service import WorksheetProcessor


def test_sanitize_ocr_math_text_integral_patterns():
    ocr_raw = """
ក.jូ 3xdx ខ.fទ4xdx
គ.j;x^2dx ឃ.}}(x^2- 5x)ix
ង.J2x2dx ។
"""
    cleaned = sanitize_ocr_math_text(ocr_raw)
    assert r"\int_{0}^{2} 3x dx" in cleaned
    assert r"\int_{1}^{4} 4x dx" in cleaned
    assert r"\int_{0}^{2} x^2 dx" in cleaned
    assert r"\int_{0}^{2} (x^2- 5x) dx" in cleaned
    assert r"\int_{1}^{2} x^2 dx" in cleaned
    assert "។" not in cleaned


def test_parse_math_text_integral_variants():
    # Definite integral with unicode
    p1 = parse_math_text(r"∫_{0}^{2} 3x dx")
    assert classify_problem(p1) == "calculus_integral"
    res1 = solve(p1, "calculus_integral")
    assert res1.answer == "6"

    # Definite integral with caret bounds
    p2 = parse_math_text(r"\int_1^4 4x dx")
    assert classify_problem(p2) == "calculus_integral"
    res2 = solve(p2, "calculus_integral")
    assert res2.answer == "30"

    # Expression ending in differential dx without \int
    p3 = parse_math_text(r"3x dx")
    assert classify_problem(p3) == "calculus_integral"
    res3 = solve(p3, "calculus_integral")
    assert "3*x**2/2" in res3.answer

    # Polynomial integrand with parentheses
    p4 = parse_math_text(r"\int_{0}^{2} (x^2 - 5x) dx")
    assert classify_problem(p4) == "calculus_integral"
    res4 = solve(p4, "calculus_integral")
    assert res4.answer == "-22/3"


def test_worksheet_processor_image4():
    from pathlib import Path
    image_path = Path("training/test_exercises/integrals/image4.png")
    if not image_path.exists():
        image_path = Path("backend/training/test_exercises/integrals/image4.png")
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    processor = WorksheetProcessor()
    result = processor.process_image(img_bytes)

    assert len(result.solved_problems) == 5
    expected_answers = ["6", "30", "8/3", "-22/3", "7/3"]

    for i, sp in enumerate(result.solved_problems):
        assert sp.problem_type == "calculus_integral"
        assert sp.error is None
        assert sp.solution is not None
        assert sp.solution.answer == expected_answers[i]
        assert sp.solution.is_verified is True
        assert len(sp.solution.steps) >= 4
