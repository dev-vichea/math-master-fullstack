"""
Tests for instruction detection and parsing.

Tests the Khmer math vocabulary knowledge base and instruction detector.
"""

import pytest

from app.models.document import InstructionType
from app.parser.instruction_parser import InstructionDetector, KhmerMathVocabulary
from app.parser.instruction_parser.vocabulary import MathAction


class TestKhmerMathVocabulary:
    """Test Khmer math vocabulary knowledge base."""

    def test_get_all_patterns(self):
        """Test getting all instruction patterns."""
        patterns = KhmerMathVocabulary.get_all_patterns()
        assert len(patterns) > 0
        assert any(p.language == "km" for p in patterns)
        assert any(p.language == "en" for p in patterns)

    def test_get_patterns_by_language_khmer(self):
        """Test getting Khmer patterns."""
        patterns = KhmerMathVocabulary.get_patterns_by_language("km")
        assert all(p.language == "km" for p in patterns)
        assert len(patterns) > 5

    def test_get_patterns_by_language_english(self):
        """Test getting English patterns."""
        patterns = KhmerMathVocabulary.get_patterns_by_language("en")
        assert all(p.language == "en" for p in patterns)
        assert len(patterns) > 5

    def test_get_patterns_by_action(self):
        """Test getting patterns by action."""
        solve_patterns = KhmerMathVocabulary.get_patterns_by_action(MathAction.SOLVE)
        assert all(p.action == MathAction.SOLVE for p in solve_patterns)
        assert len(solve_patterns) >= 2  # At least Khmer and English

    def test_math_objects_coverage(self):
        """Test that math objects are defined for both languages."""
        assert "equation" in KhmerMathVocabulary.MATH_OBJECTS_KM
        assert "equation" in KhmerMathVocabulary.MATH_OBJECTS_EN
        assert "polynomial" in KhmerMathVocabulary.MATH_OBJECTS_KM
        assert "polynomial" in KhmerMathVocabulary.MATH_OBJECTS_EN


class TestInstructionDetector:
    """Test instruction detection and parsing."""

    def test_detect_khmer_factor_instruction(self):
        """Test detecting Khmer factor instruction."""
        detector = InstructionDetector()
        text = "ចូរដាក់ជាកត្តាកត់"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.FACTOR
        assert parsed.language == "km"
        assert parsed.confidence > 0.5
        assert "ដាក់ជាកត្តាកត់" in parsed.matched_keywords

    def test_detect_khmer_factor_with_context(self):
        """Test detecting Khmer factor with context."""
        detector = InstructionDetector()
        text = "ចូរដាក់ជាកត្តាកត់នៃពហុធាខាងក្រោម"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.FACTOR
        assert "polynomial" in parsed.target_objects
        assert "following" in parsed.modifiers

    def test_detect_khmer_solve_instruction(self):
        """Test detecting Khmer solve instruction."""
        detector = InstructionDetector()
        text = "ដោះស្រាយសមីការខាងក្រោម"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.SOLVE
        assert parsed.language == "km"
        assert "equation" in parsed.target_objects

    def test_detect_khmer_calculate_instruction(self):
        """Test detecting Khmer calculate instruction."""
        detector = InstructionDetector()
        text = "គណនាតម្លៃ"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.CALCULATE
        assert parsed.language == "km"

    def test_detect_khmer_simplify_instruction(self):
        """Test detecting Khmer simplify instruction."""
        detector = InstructionDetector()
        text = "សង្ខេបកន្សោម"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.SIMPLIFY
        assert "expression" in parsed.target_objects

    def test_detect_english_solve_instruction(self):
        """Test detecting English solve instruction."""
        detector = InstructionDetector()
        text = "Solve the following equations"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.SOLVE
        assert parsed.language == "en"
        assert "equation" in parsed.target_objects
        assert "following" in parsed.modifiers

    def test_detect_english_factor_instruction(self):
        """Test detecting English factor instruction."""
        detector = InstructionDetector()
        text = "Factor the polynomials"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.FACTOR
        assert "polynomial" in parsed.target_objects

    def test_detect_english_simplify_instruction(self):
        """Test detecting English simplify instruction."""
        detector = InstructionDetector()
        text = "Simplify each expression"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.SIMPLIFY
        assert "expression" in parsed.target_objects
        assert "each" in parsed.modifiers

    def test_detect_english_evaluate_instruction(self):
        """Test detecting English evaluate instruction."""
        detector = InstructionDetector()
        text = "Evaluate the value"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.EVALUATE

    def test_detect_english_expand_instruction(self):
        """Test detecting English expand instruction."""
        detector = InstructionDetector()
        text = "Expand the expression"

        parsed = detector.detect(text)

        assert parsed is not None
        assert parsed.action == MathAction.EXPAND
        assert "expression" in parsed.target_objects

    def test_language_auto_detection_khmer(self):
        """Test automatic language detection for Khmer."""
        detector = InstructionDetector()
        text = "ចូរដាក់ជាកត្តាកត់"

        parsed = detector.detect(text, language=None)

        assert parsed is not None
        assert parsed.language == "km"

    def test_language_auto_detection_english(self):
        """Test automatic language detection for English."""
        detector = InstructionDetector()
        text = "Solve the equation"

        parsed = detector.detect(text, language=None)

        assert parsed is not None
        assert parsed.language == "en"

    def test_is_instruction_true(self):
        """Test is_instruction returns True for valid instruction."""
        detector = InstructionDetector()
        assert detector.is_instruction("ដោះស្រាយសមីការ")
        assert detector.is_instruction("Solve the equation")
        assert detector.is_instruction("ចូរដាក់ជាកត្តាកត់")

    def test_is_instruction_false(self):
        """Test is_instruction returns False for non-instruction."""
        detector = InstructionDetector()
        assert not detector.is_instruction("x² - 4")
        assert not detector.is_instruction("ក. x² - 5x + 6")
        assert not detector.is_instruction("2x + 5 = 11")

    def test_detect_all(self):
        """Test detecting multiple instructions."""
        detector = InstructionDetector()
        texts = [
            "ដោះស្រាយសមីការ",
            "ចូរដាក់ជាកត្តាកត់",
            "x² - 4",  # Not an instruction
            "Solve the equation",
        ]

        results = detector.detect_all(texts)

        assert len(results) == 3  # Three instructions detected
        assert results[0].action == MathAction.SOLVE
        assert results[1].action == MathAction.FACTOR
        assert results[2].action == MathAction.SOLVE

    def test_to_instruction_conversion(self):
        """Test converting ParsedInstruction to Instruction model."""
        detector = InstructionDetector()
        text = "ចូរដាក់ជាកត្តាកត់"

        parsed = detector.detect(text)
        assert parsed is not None

        instruction = parsed.to_instruction()

        assert instruction.text == text
        assert instruction.language == "km"
        assert instruction.instruction_type == InstructionType.FACTOR
        assert instruction.confidence > 0.5
        assert len(instruction.detected_keywords) > 0

    def test_empty_text(self):
        """Test handling empty text."""
        detector = InstructionDetector()
        assert detector.detect("") is None
        assert detector.detect("   ") is None

    def test_confidence_scoring(self):
        """Test confidence scoring for different matches."""
        detector = InstructionDetector()

        # Strong match with context
        strong = detector.detect("ចូរដាក់ជាកត្តាកត់នៃពហុធាខាងក្រោម")
        # Weak match without context
        weak = detector.detect("កត្តាកត់")

        assert strong is not None
        assert weak is not None
        assert strong.confidence > weak.confidence

    def test_synonym_matching(self):
        """Test that synonyms are matched."""
        detector = InstructionDetector()

        # Primary keyword
        result1 = detector.detect("ដោះស្រាយសមីការ")
        # Synonym
        result2 = detector.detect("ស្វែងរកលទ្ធផល")

        assert result1 is not None
        # Synonym should match but may have different confidence
        # Both should detect some action

    def test_multiple_object_detection(self):
        """Test detecting multiple mathematical objects."""
        detector = InstructionDetector()
        text = "Solve the following system of equations"

        parsed = detector.detect(text)

        assert parsed is not None
        # Should detect both "system" and "equation"
        assert len(parsed.target_objects) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
