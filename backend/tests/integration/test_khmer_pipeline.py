from app.core.khmer.digits import khmer_digits_to_arabic
from app.core.khmer.extractor import extract_expression
from app.core.khmer.intent import MathIntent, RuleBasedIntentClassifier
from app.core.khmer.normalizer import normalize_khmer_text
from app.core.parser.expression_parser import parse_math_text


def test_khmer_digit_conversion():
    assert khmer_digits_to_arabic("១៥") == "15"
    assert khmer_digits_to_arabic("abc១២៣xyz") == "abc123xyz"


def test_normalize_khmer_text_converts_digits_and_punctuation():
    normalized = normalize_khmer_text("ដោះស្រាយ ២x + ៥ = ១៥៖")
    assert "2x" in normalized.replace(" ", "")
    assert "15" in normalized
    assert "៖" not in normalized


def test_extract_expression_from_khmer_sentence():
    normalized = normalize_khmer_text("ដោះស្រាយសមីការនេះ 2x + 5 = 15")
    expression = extract_expression(normalized)
    assert expression is not None
    assert expression.replace(" ", "") == "2x+5=15" or "2x+5=15" in expression.replace(" ", "")


def test_intent_classifier_detects_solve():
    classifier = RuleBasedIntentClassifier()
    assert classifier.classify("ដោះស្រាយ 2x + 5 = 15") == MathIntent.SOLVE_EQUATION
    assert classifier.classify("2x+5=15") == MathIntent.SOLVE_EQUATION


def test_intent_classifier_detects_evaluate():
    classifier = RuleBasedIntentClassifier()
    assert classifier.classify("3 + 4 * 2") == MathIntent.EVALUATE_EXPRESSION


def test_intent_classifier_unknown_for_non_math_text():
    classifier = RuleBasedIntentClassifier()
    assert classifier.classify("សួស្តី តើអ្នកសុខសប្បាយទេ") == MathIntent.UNKNOWN


def test_parser_handles_implicit_multiplication_and_caret_power():
    parsed = parse_math_text("2x^2+3x=5")
    assert parsed.is_equation
    assert str(parsed.sympy_expr) == "Eq(2*x**2 + 3*x, 5)"
