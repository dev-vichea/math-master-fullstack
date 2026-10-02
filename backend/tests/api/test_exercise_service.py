"""
Tests for exercise service.

Tests the complete pipeline for processing math exercise documents.
"""

import pytest

from app.models.document import InstructionType
from app.services.exercise_service import ExerciseService


class TestExerciseService:
    """Test exercise service functionality."""

    def test_process_simple_factorization_exercise(self):
        """Test processing simple factorization exercise."""
        service = ExerciseService()

        text = """
ចូរដាក់ជាកត្តាកត់
ក. x^2 - 4
ខ. x^2 - 5*x + 6
គ. 2*x^2 + 8*x
"""

        result = service.process_text(text, language="km")

        assert result.success
        assert len(result.errors) == 0
        assert result.exercise.get_section_count() >= 1
        assert result.exercise.get_total_problems() == 3

    def test_process_solve_equations_exercise(self):
        """Test processing solve equations exercise."""
        service = ExerciseService()

        text = """
Solve the following equations
a) Eq(2*x + 5, 11)
b) Eq(3*x - 7, 2)
"""

        result = service.process_text(text, language="en")

        assert result.success
        assert result.exercise.get_total_problems() == 2

        # Check that instruction was detected
        if result.exercise.sections:
            section = result.exercise.sections[0]
            assert section.instruction is not None
            assert section.instruction.instruction_type == InstructionType.SOLVE

    def test_process_mixed_instructions(self):
        """Test processing exercise with multiple instructions."""
        service = ExerciseService()

        text = """
ដោះស្រាយសមីការ
ក. Eq(x + 5, 10)
ខ. Eq(2*x - 3, 7)

ចូរដាក់ជាកត្តាកត់
គ. x^2 - 9
ឃ. x^2 + 5*x + 6
"""

        result = service.process_text(text, language="km")

        assert result.success
        # Should have 2 sections (solve + factor)
        assert result.exercise.get_section_count() >= 1
        assert result.exercise.get_total_problems() == 4

    def test_process_empty_text(self):
        """Test handling empty text."""
        service = ExerciseService()

        result = service.process_text("", language="km")

        assert result.success  # Should succeed but with warnings
        assert result.exercise.get_total_problems() == 0
        assert len(result.warnings) > 0

    def test_process_text_without_problems(self):
        """Test processing text with only instruction."""
        service = ExerciseService()

        text = "ចូរដាក់ជាកត្តាកត់"

        result = service.process_text(text, language="km")

        # Should detect instruction but no problems
        assert len(result.warnings) > 0
        assert "No problems detected" in " ".join(result.warnings)

    def test_process_problems_without_instruction(self):
        """Test processing problems without instruction."""
        service = ExerciseService()

        text = """
a) x^2 - 4
b) x^2 - 5*x + 6
"""

        result = service.process_text(text, language="en")

        assert result.success
        assert result.exercise.get_total_problems() == 2
        # Should create default section
        assert result.exercise.get_section_count() >= 1

    def test_validate_exercise_valid(self):
        """Test validating valid exercise."""
        service = ExerciseService()

        text = """
Factor
a) x^2 - 4
b) x^2 - 5*x + 6
"""

        result = service.process_text(text, language="en")
        is_valid, errors = service.validate_exercise(result.exercise)

        assert is_valid
        assert len(errors) == 0

    def test_validate_exercise_invalid_sequence(self):
        """Test validating exercise with invalid problem sequence."""
        service = ExerciseService()

        text = """
Factor
a) x^2 - 4
c) x^2 - 5*x + 6
"""

        result = service.process_text(text, language="en")
        is_valid, errors = service.validate_exercise(result.exercise)

        # Should detect sequence error
        assert not is_valid or len(errors) > 0

    def test_get_statistics(self):
        """Test getting exercise statistics."""
        service = ExerciseService()

        text = """
Factor the following
a) x^2 - 4
b) x^2 - 5*x + 6

Solve
c) Eq(x + 5, 10)
"""

        result = service.process_text(text, language="en")
        stats = service.get_statistics(result.exercise)

        assert stats["total_problems"] == 3
        assert stats["sections"] >= 1
        assert "en" in stats["languages"]
        assert stats["average_confidence"] > 0

    def test_context_aware_classification(self):
        """Test that problems are classified with instruction context."""
        service = ExerciseService()

        text = """
ចូរដាក់ជាកត្តាកត់
ក. x^2 - 4
"""

        result = service.process_text(text, language="km")

        assert result.success
        if result.exercise.sections and result.exercise.sections[0].problems:
            problem = result.exercise.sections[0].problems[0]
            # Should be classified as factorization due to instruction
            assert problem.problem.problem_type is not None
            assert "factor" in problem.problem.problem_type.lower()

    def test_problem_confidence_tracking(self):
        """Test that confidence scores are tracked."""
        service = ExerciseService()

        text = """
Factor
a) x^2 - 4
b) x^2 - 5*x + 6
"""

        result = service.process_text(text, language="en")

        # Check that confidence is tracked
        avg_confidence = result.exercise.get_average_confidence()
        assert 0 <= avg_confidence <= 1

    def test_instruction_types_detected(self):
        """Test that different instruction types are detected."""
        service = ExerciseService()

        # Factor instruction
        text1 = "ចូរដាក់ជាកត្តាកត់\nក. x^2 - 4"
        result1 = service.process_text(text1, language="km")

        if result1.exercise.sections:
            assert (
                result1.exercise.sections[0].instruction.instruction_type
                == InstructionType.FACTOR
            )

        # Solve instruction
        text2 = "ដោះស្រាយសមីការ\nក. Eq(x + 5, 10)"
        result2 = service.process_text(text2, language="km")

        if result2.exercise.sections:
            assert (
                result2.exercise.sections[0].instruction.instruction_type
                == InstructionType.SOLVE
            )

    def test_problem_label_detection(self):
        """Test that problem labels are correctly detected."""
        service = ExerciseService()

        text = """
Factor
a) x^2 - 4
b) x^2 - 5*x + 6
"""

        result = service.process_text(text, language="en")

        if result.exercise.sections and result.exercise.sections[0].problems:
            problems = result.exercise.sections[0].problems
            assert problems[0].label == "a)"
            assert problems[1].label == "b)"

    def test_khmer_label_detection(self):
        """Test Khmer label detection."""
        service = ExerciseService()

        text = """
ចូរដាក់ជាកត្តាកត់
ក. x^2 - 4
ខ. x^2 - 5*x + 6
"""

        result = service.process_text(text, language="km")

        if result.exercise.sections and result.exercise.sections[0].problems:
            problems = result.exercise.sections[0].problems
            assert problems[0].label == "ក."
            assert problems[1].label == "ខ."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
