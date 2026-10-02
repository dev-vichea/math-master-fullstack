"""
Tests for problem extraction.

Tests detection of problem labels and extraction of mathematical expressions.
"""

import pytest

from app.models.document import BoundingBox, ProblemLabel
from app.models.problem import ProblemSource
from app.ocr.layout.reading_order import TextBlock
from app.parser.problem_extractor import ProblemExtractor


class TestProblemExtractor:
    """Test problem extraction functionality."""

    def test_extract_latin_lowercase_problems(self):
        """Test extracting problems with Latin lowercase labels."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b) x² - 5x + 6
c) 2x² + 8x
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 3
        assert problems[0].label == "a)"
        assert problems[0].label_type == ProblemLabel.LATIN_LOWER
        assert problems[0].content == "x² - 4"

        assert problems[1].label == "b)"
        assert problems[1].content == "x² - 5x + 6"

        assert problems[2].label == "c)"
        assert problems[2].content == "2x² + 8x"

    def test_extract_latin_uppercase_problems(self):
        """Test extracting problems with Latin uppercase labels."""
        extractor = ProblemExtractor()
        text = """
A) 3x + 5 = 11
B) 2x - 7 = 9
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 2
        assert problems[0].label == "A)"
        assert problems[0].label_type == ProblemLabel.LATIN_UPPER
        assert problems[1].label == "B)"

    def test_extract_khmer_problems(self):
        """Test extracting problems with Khmer labels."""
        extractor = ProblemExtractor()
        text = """
ក. x² - 4
ខ. x² - 5x + 6
គ. 3x² - 9x + x³
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 3
        assert problems[0].label == "ក."
        assert problems[0].label_type == ProblemLabel.KHMER
        assert problems[0].content == "x² - 4"

        assert problems[1].label == "ខ."
        assert problems[1].content == "x² - 5x + 6"

        assert problems[2].label == "គ."
        assert problems[2].content == "3x² - 9x + x³"

    def test_extract_numeric_problems(self):
        """Test extracting problems with numeric labels."""
        extractor = ProblemExtractor()
        text = """
1) x + 5 = 10
2) 2x - 3 = 7
3) x² = 16
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 3
        assert problems[0].label == "1)"
        assert problems[0].label_type == ProblemLabel.NUMERIC
        assert problems[1].label == "2)"
        assert problems[2].label == "3)"

    def test_extract_roman_lowercase_problems(self):
        """Test extracting problems with Roman lowercase labels."""
        extractor = ProblemExtractor()
        text = """
i) x + 1 = 2
ii) x + 2 = 4
iii) x + 3 = 6
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 3
        assert problems[0].label == "i)"
        assert problems[0].label_type == ProblemLabel.ROMAN_LOWER

    def test_extract_dot_separator(self):
        """Test extracting problems with dot separator."""
        extractor = ProblemExtractor()
        text = """
a. x² - 4
b. x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 2
        assert problems[0].label == "a."
        assert problems[1].label == "b."

    def test_extract_khmer_special_punctuation(self):
        """Test extracting Khmer problems with Khmer punctuation."""
        extractor = ProblemExtractor()
        text = """
ក។ x² - 4
ខ។ x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 2
        assert problems[0].label == "ក។"
        assert problems[1].label == "ខ។"

    def test_extract_from_blocks(self):
        """Test extracting problems from text blocks with spatial info."""
        extractor = ProblemExtractor()

        blocks = [
            TextBlock(
                text="a) x² - 4",
                bounding_box=BoundingBox(x=0.1, y=0.2, width=0.3, height=0.05),
                confidence=0.95,
            ),
            TextBlock(
                text="b) x² - 5x + 6",
                bounding_box=BoundingBox(x=0.1, y=0.3, width=0.4, height=0.05),
                confidence=0.92,
            ),
        ]

        problems = extractor.extract_from_blocks(blocks)

        assert len(problems) == 2
        assert problems[0].bounding_box is not None
        assert problems[0].bounding_box.x == 0.1
        assert problems[0].confidence == 0.95
        assert problems[1].confidence == 0.92

    def test_detect_label_type(self):
        """Test detecting label type from text."""
        extractor = ProblemExtractor()

        assert extractor.detect_label_type("a) x² - 4") == ProblemLabel.LATIN_LOWER
        assert extractor.detect_label_type("A) x² - 4") == ProblemLabel.LATIN_UPPER
        assert extractor.detect_label_type("ក. x² - 4") == ProblemLabel.KHMER
        assert extractor.detect_label_type("1) x² - 4") == ProblemLabel.NUMERIC
        assert extractor.detect_label_type("i) x² - 4") == ProblemLabel.ROMAN_LOWER
        assert extractor.detect_label_type("no label here") is None

    def test_is_problem_line(self):
        """Test checking if line contains problem label."""
        extractor = ProblemExtractor()

        assert extractor.is_problem_line("a) x² - 4")
        assert extractor.is_problem_line("ក. x² - 5x + 6")
        assert extractor.is_problem_line("1) 2x + 5 = 11")
        assert not extractor.is_problem_line("x² - 4")
        assert not extractor.is_problem_line("ដោះស្រាយសមីការ")

    def test_group_by_label_type(self):
        """Test grouping problems by label type."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b) x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)
        groups = extractor.group_by_label_type(problems)

        assert len(groups) == 1
        assert ProblemLabel.LATIN_LOWER in groups
        assert len(groups[ProblemLabel.LATIN_LOWER]) == 2

    def test_to_math_problems(self):
        """Test converting extracted problems to Problem objects."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b) x² - 5x + 6
"""
        extracted = extractor.extract_from_text(text)
        problems = extractor.to_math_problems(extracted, language="km", source=ProblemSource.MANUAL)

        assert len(problems) == 2
        assert problems[0].label == "a)"
        assert problems[0].problem.raw_input == "x² - 4"
        assert problems[0].problem.language == "km"
        assert problems[0].problem.source == ProblemSource.MANUAL
        assert problems[0].reading_order == 0
        assert problems[1].reading_order == 1

    def test_extract_label_sequence(self):
        """Test extracting label sequence."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b) x² - 5x + 6
c) 2x² + 8x
"""
        problems = extractor.extract_from_text(text)
        labels = extractor.extract_label_sequence(problems)

        assert labels == ["a", "b", "c"]

    def test_validate_sequence_valid(self):
        """Test validating valid problem sequence."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b) x² - 5x + 6
c) 2x² + 8x
"""
        problems = extractor.extract_from_text(text)
        is_valid, error = extractor.validate_sequence(problems)

        assert is_valid
        assert error == ""

    def test_validate_sequence_invalid_order(self):
        """Test validating invalid problem sequence (wrong order)."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
c) x² - 5x + 6
b) 2x² + 8x
"""
        problems = extractor.extract_from_text(text)
        is_valid, error = extractor.validate_sequence(problems)

        assert not is_valid
        assert "Expected 'b'" in error

    def test_validate_sequence_numeric(self):
        """Test validating numeric sequence."""
        extractor = ProblemExtractor()
        text = """
1) x² - 4
2) x² - 5x + 6
3) 2x² + 8x
"""
        problems = extractor.extract_from_text(text)
        is_valid, error = extractor.validate_sequence(problems)

        assert is_valid

    def test_validate_sequence_khmer(self):
        """Test validating Khmer sequence."""
        extractor = ProblemExtractor()
        text = """
ក. x² - 4
ខ. x² - 5x + 6
គ. 2x² + 8x
"""
        problems = extractor.extract_from_text(text)
        is_valid, error = extractor.validate_sequence(problems)

        assert is_valid

    def test_empty_text(self):
        """Test handling empty text."""
        extractor = ProblemExtractor()
        problems = extractor.extract_from_text("")

        assert len(problems) == 0

    def test_text_without_problems(self):
        """Test handling text without problems."""
        extractor = ProblemExtractor()
        text = "ដោះស្រាយសមីការខាងក្រោម"
        problems = extractor.extract_from_text(text)

        assert len(problems) == 0

    def test_label_without_content(self):
        """Test handling label without content."""
        extractor = ProblemExtractor()
        text = "a)"
        problems = extractor.extract_from_text(text)

        # Should not extract labels without content
        assert len(problems) == 0

    def test_mixed_label_styles(self):
        """Test handling mixed label styles."""
        extractor = ProblemExtractor()
        text = """
a) x² - 4
b. x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)

        # Should extract both despite different punctuation
        assert len(problems) == 2
        assert problems[0].label == "a)"
        assert problems[1].label == "b."

    def test_whitespace_handling(self):
        """Test handling whitespace around labels."""
        extractor = ProblemExtractor()
        text = """
  a)   x² - 4
    b)  x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 2
        assert problems[0].content == "x² - 4"
        assert problems[1].content == "x² - 5x + 6"

    def test_complex_expressions(self):
        """Test extracting complex mathematical expressions."""
        extractor = ProblemExtractor()
        text = """
a) x² - 5x + 6 = 0
b) (x + 1)(x - 2) = 0
c) 2x³ - 3x² + 4x - 5
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 3
        assert "=" in problems[0].content
        assert "(" in problems[1].content
        assert "³" in problems[2].content

    def test_khmer_extended_labels(self):
        """Test Khmer labels beyond first few letters."""
        extractor = ProblemExtractor()
        text = """
ឃ. x² - 4
ង. x² - 5x + 6
"""
        problems = extractor.extract_from_text(text)

        assert len(problems) == 2
        assert problems[0].label == "ឃ."
        assert problems[1].label == "ង."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
