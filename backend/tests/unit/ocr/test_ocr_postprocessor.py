"""
Unit tests for OCR post-processor and math text sanitizer.
"""
import pytest

from app.ocr.normalization.ocr_postprocessor import sanitize_ocr_math_text


def test_sanitize_unicode_superscripts():
    assert sanitize_ocr_math_text("x² + 5x + 6 = 0") == "x^2 + 5x + 6 = 0"
    assert sanitize_ocr_math_text("x³ - 6x² + 11x - 6 = 0") == "x^3 - 6x^2 + 11x - 6 = 0"
    assert sanitize_ocr_math_text("y⁴ = 16") == "y^4 = 16"
    assert sanitize_ocr_math_text("x⁻¹ + 2 = 5") == "x^-1 + 2 = 5"


def test_sanitize_collapsed_exponents():
    # Standard quadratic from OCR missing caret
    assert sanitize_ocr_math_text("x2 - 25x + 15=0") == "x^2 - 25x + 15=0"
    assert sanitize_ocr_math_text("10x2 + 8x = 32") == "10x^2 + 8x = 32"
    assert sanitize_ocr_math_text("x2 = 9") == "x^2 = 9"
    assert sanitize_ocr_math_text("x3 + 2x2 - x = 0") == "x^3 + 2x^2 - x = 0"


def test_sanitize_math_operators():
    # Unicode minus
    assert sanitize_ocr_math_text("2x − 4 = 10") == "2x - 4 = 10"
    assert sanitize_ocr_math_text("5 – 3 = 2") == "5 - 3 = 2"
    assert sanitize_ocr_math_text("10 — 2 = 8") == "10 - 2 = 8"

    # Multiplication
    assert sanitize_ocr_math_text("3 × x + 5 = 20") == "3 * x + 5 = 20"
    assert sanitize_ocr_math_text("2 · x - 4 = 10") == "2 * x - 4 = 10"
    assert sanitize_ocr_math_text("4 ✕ 5 = 20") == "4 * 5 = 20"

    # Division
    assert sanitize_ocr_math_text("12 ÷ 3 + 2 = 6") == "12 / 3 + 2 = 6"
    assert sanitize_ocr_math_text("15 : 3 = 5") == "15 / 3 = 5"

    # Inequalities
    assert sanitize_ocr_math_text("2x ≤ 10") == "2x <= 10"
    assert sanitize_ocr_math_text("3x ≥ 15") == "3x >= 15"
    assert sanitize_ocr_math_text("x ≠ 0") == "x != 0"


def test_sanitize_khmer_numerals_and_punctuation():
    assert sanitize_ocr_math_text("២x + ៥ = ១៥") == "2x + 5 = 15"
    assert sanitize_ocr_math_text("លំហាត់ទី 1 ៖ 2x = 4") == "លំហាត់ទី 1 : 2x = 4"


def test_sanitize_broken_ocr_spacing():
    assert sanitize_ocr_math_text("2 x + 5 = 1 5") == "2x + 5 = 15"
    assert sanitize_ocr_math_text("1 0 0 - 2 5 = 7 5") == "100 - 25 = 75"


def test_sanitize_character_confusions():
    # Letter O in numbers
    assert sanitize_ocr_math_text("2O + 1O = 30") == "20 + 10 = 30"
    assert sanitize_ocr_math_text("1OO / 2 = 5O") == "100 / 2 = 50"
