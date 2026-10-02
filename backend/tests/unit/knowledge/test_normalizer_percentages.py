"""
Unit tests for the percentage conversion in the normalizer.

Tests the convert_percentages_to_decimals function directly.
"""
from app.core.khmer.normalizer import convert_percentages_to_decimals


def test_simple_percentage_conversion():
    """Test basic percentage conversion: 20% -> (20/100)"""
    result = convert_percentages_to_decimals("20%")
    assert result == "(20/100)"


def test_percentage_with_space():
    """Test percentage with space: 20 % -> (20/100)"""
    result = convert_percentages_to_decimals("20 %")
    assert result == "(20/100)"


def test_khmer_percentage_word():
    """Test Khmer percentage word: 20 ភាគរយ -> (20/100)"""
    result = convert_percentages_to_decimals("20 ភាគរយ")
    assert result == "(20/100)"


def test_percentage_of_pattern():
    """Test 'X% of Y' pattern: 20% of 150 -> (20/100)*150"""
    result = convert_percentages_to_decimals("20% of 150")
    assert result == "(20/100)*150"


def test_khmer_percentage_of_pattern():
    """Test Khmer 'X ភាគរយ នៃ Y' pattern"""
    result = convert_percentages_to_decimals("20 ភាគរយ នៃ 150")
    assert result == "(20/100)*150"


def test_decimal_percentage():
    """Test decimal percentage: 12.5% -> (12.5/100)"""
    result = convert_percentages_to_decimals("12.5%")
    assert result == "(12.5/100)"


def test_multiple_percentages():
    """Test multiple percentages in expression: 50% + 25% -> (50/100) + (25/100)"""
    result = convert_percentages_to_decimals("50% + 25%")
    assert result == "(50/100) + (25/100)"


def test_no_percentage():
    """Test text without percentage remains unchanged"""
    result = convert_percentages_to_decimals("3/4 + 1/2")
    assert result == "3/4 + 1/2"


def test_percentage_over_100():
    """Test percentage over 100: 150% -> (150/100)"""
    result = convert_percentages_to_decimals("150%")
    assert result == "(150/100)"


def test_percentage_case_insensitive():
    """Test that 'of' is case insensitive: 20% OF 100"""
    result = convert_percentages_to_decimals("20% OF 100")
    assert result == "(20/100)*100"
