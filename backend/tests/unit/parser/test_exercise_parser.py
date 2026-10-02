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
