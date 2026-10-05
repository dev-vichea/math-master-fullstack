"""
Tests for bilingual exercise parser (Khmer & English).
"""
import pytest

from app.core.khmer.exercise_parser import parse_exercise
from app.services.math_service import process_question


def test_parse_khmer_exercise_header_and_instruction():
    text = "លំហាត់ទី 1 ៖ ដោះស្រាយសមីការ 3x - 6 = 9"
    parsed = parse_exercise(text)

    assert parsed.exercise_title == "លំហាត់ទី 1"
    assert "ដោះស្រាយសមីការ" in (parsed.instruction or "")
    assert parsed.primary_expression == "3x-6=9"
    assert parsed.detected_intent == "solve_equation"

    # Solve via pipeline
    res = process_question(text)
    assert res.answer == "5"


def test_parse_english_exercise_header_and_instruction():
    text = "Exercise 1: Solve for x: 2x + 5 = 15"
    parsed = parse_exercise(text)

    assert parsed.exercise_title == "Exercise 1"
    assert "Solve for x" in (parsed.instruction or "")
    assert parsed.primary_expression == "2x+5=15"
    assert parsed.detected_intent == "solve_equation"

    res = process_question(text)
    assert res.answer == "5"


def test_prompt_variable_isolation_prevents_x4x_collision():
    # Crucial test: "Find the value of x if 4x + 10 = 30" must NOT become x4x+10=30
    text = "Exercise (លំហាត់): Find the value of x if 4x + 10 = 30"
    parsed = parse_exercise(text)

    assert parsed.primary_expression == "4x+10=30"
    res = process_question(text)
    assert res.problem_type == "linear_equation"
    assert res.answer == "5"


def test_find_x_colon_pattern():
    text = "Find x: 2x + 10 = 20"
    parsed = parse_exercise(text)

    assert parsed.primary_expression == "2x+10=20"
    res = process_question(text)
    assert res.answer == "5"


def test_simplify_english_command():
    text = "Simplify: 3x + 5x - 2"
    parsed = parse_exercise(text)

    assert parsed.primary_expression == "3x+5x-2"
    assert parsed.detected_intent == "simplify_expression"
    res = process_question(text)
    assert res.answer == "8*x - 2"


def test_sub_exercises_khmer():
    text = "លំហាត់ទី ១\nក. 2x + 4 = 12\nខ) 3x - 9 = 0"
    parsed = parse_exercise(text)

    assert parsed.exercise_title == "លំហាត់ទី 1"
    assert len(parsed.sub_exercises) == 2
    assert parsed.sub_exercises[0].label == "ក"
    assert parsed.sub_exercises[0].expression == "2x+4=12"
    assert parsed.sub_exercises[1].label == "ខ"
    assert parsed.sub_exercises[1].expression == "3x-9=0"
    assert parsed.primary_expression == "2x+4=12"


def test_sub_exercises_english():
    text = "Exercise 2.\na) 2x + 5 = 15\nb) x^2 - 4 = 0"
    parsed = parse_exercise(text)

    assert parsed.exercise_title == "Exercise 2"
    assert len(parsed.sub_exercises) == 2
    assert parsed.sub_exercises[0].label == "a"
    assert parsed.sub_exercises[0].expression == "2x+5=15"
    assert parsed.sub_exercises[1].label == "b"
    assert parsed.sub_exercises[1].expression == "x^2-4=0"


def test_autonomous_numbered_instruction_and_subproblem():
    """Verify that a numbered instruction line with OCR artifacts is not mistaken for a sub-exercise."""
    text = (
        r"1. ធ្ទៀងផ្ទាត់ថាអនុគមន៍ / ជាចម្លើយនៃសមីការឌីផេរំង័ពស្បួលដែលគេឱ្យនៅខាងស្ដាំ : "
        r"ក. f(x) = (2x+1)e^{-x} , y^{\prime\prime}+2y^{\prime}+y = 0"
    )
    parsed = parse_exercise(text)

    # Must NOT have a sub-exercise with label '1' or expression '/'
    assert all(sub.expression != "/" for sub in parsed.sub_exercises)
    assert len(parsed.sub_exercises) == 1
    assert parsed.sub_exercises[0].label == "ក"
    assert "y''" in parsed.sub_exercises[0].expression
    assert "f(x)" in parsed.sub_exercises[0].expression
    assert parsed.primary_expression == parsed.sub_exercises[0].expression
    assert "ផ្ទៀងផ្ទាត់" in (parsed.instruction or "")


def test_autonomous_unknown_instruction_without_math():
    """Verify system autonomously treats a leading non-math line as instruction header even with unknown words."""
    text = "1. ពាក្យណែនាំទូទៅមិនស្គាល់ខ្លះៗ : ក. 3x + 6 = 12"
    parsed = parse_exercise(text)

    assert len(parsed.sub_exercises) == 1
    assert parsed.sub_exercises[0].label == "ក"
    assert parsed.sub_exercises[0].expression == "3x+6=12"


def test_clean_math_only_removes_khmer_and_extracts_minimal_math():
    from app.parser.exercise_parser.exercise_parser import clean_math_only

    raw = r"គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម : ឌ, = - - - .(x - - + 3x + 1)"
    cleaned = clean_math_only(raw)
    assert not any("\u1780" <= c <= "\u17ff" for c in cleaned)
    assert "(x" in cleaned and "3x" in cleaned

    derivative_raw = r"គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម ៈ ឃ. y = \frac{1}{(x^2 + 3x + 1)^2}"
    cleaned_deriv = clean_math_only(derivative_raw)
    assert cleaned_deriv == r"y = \frac{1}{(x^2 + 3x + 1)^2}"

    aligned_raw = r"\begin{aligned} & \text{គណនា } \\ & y = 2x^2 - x + 1 \end{aligned}"
    assert clean_math_only(aligned_raw) == "y = 2x^2 - x + 1"

