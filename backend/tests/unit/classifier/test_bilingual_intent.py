"""
Tests for bilingual intent classification (Khmer and English).
"""
import pytest

from app.core.khmer.intent import MathIntent, RuleBasedIntentClassifier


@pytest.fixture
def classifier():
    return RuleBasedIntentClassifier()


def test_english_solve_keywords(classifier):
    assert classifier.classify("Solve for x: 2x + 5 = 15") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("Find the value of x: 4x = 20") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("Determine x in 3x - 6 = 0") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("Find the root of 2x - 8 = 0") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("Solve the equation 5x + 10 = 35") == MathIntent.SOLVE_EQUATION


def test_english_simplify_keywords(classifier):
    assert classifier.classify("Simplify 3x + 5x - 2") == MathIntent.SIMPLIFY_EXPRESSION
    assert classifier.classify("Reduce 4x/8") == MathIntent.SIMPLIFY_EXPRESSION
    assert classifier.classify("Factorize x^2 - 5x + 6") == MathIntent.SIMPLIFY_EXPRESSION
    assert classifier.classify("Expand (x + 2)(x + 3)") == MathIntent.SIMPLIFY_EXPRESSION


def test_english_evaluate_keywords(classifier):
    assert classifier.classify("Calculate 12 * (3 + 4)") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("Evaluate 15 / 3 + 2") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("Compute the sum of 10 and 25") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("What is 10 + 20") == MathIntent.EVALUATE_EXPRESSION


def test_bilingual_fractions_and_percentages(classifier):
    assert classifier.classify("Calculate 25% of 200") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("What is the percentage: 15% + 20%") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("Fraction addition: 3/4 + 1/2") == MathIntent.EVALUATE_EXPRESSION
    assert classifier.classify("គណនាប្រភាគ 1/2 + 2/3") == MathIntent.EVALUATE_EXPRESSION


def test_mixed_bilingual_queries(classifier):
    assert classifier.classify("Exercise 1 (លំហាត់ទី 1): Solve 2x + 10 = 20") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("លំហាត់ទី 2: Simplify 4x + 2x - 1") == MathIntent.SIMPLIFY_EXPRESSION
