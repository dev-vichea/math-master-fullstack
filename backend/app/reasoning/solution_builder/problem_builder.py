"""
Problem builder integrating normalization, parsing, and classification.

This module provides the main entry point for creating MathProblem objects
from raw input (OCR or typed text). It orchestrates:
1. Text normalization with confidence tracking
2. Mathematical parsing
3. Problem classification with characteristics detection
4. MathProblem construction with full metadata
"""

from __future__ import annotations

from app.classifier.problem_classifier.classifier_enhanced import classify_with_characteristics
from app.classifier.problem_classifier.intent_classifier import RuleBasedIntentClassifier
from app.models.problem import MathProblem, ProblemSource
from app.parser.expression_parser.khmer_extractor import extract_expression
from app.parser.math_parser.expression_parser import ExpressionParseError, parse_math_text
from app.parser.pipeline import normalize_text
from app.utils.exceptions import MathProcessingError


class ProblemBuilder:
    """
    Builds MathProblem objects from raw input text.

    Integrates the full pipeline: normalization → extraction → parsing → classification
    """

    def __init__(self):
        """Initialize builder with dependencies."""
        self.intent_classifier = RuleBasedIntentClassifier()

    def build_from_text(
        self,
        text: str,
        language: str = "km",
        source: ProblemSource = ProblemSource.MANUAL,
        ocr_confidence: float | None = None,
    ) -> MathProblem:
        """
        Build a MathProblem from raw text input.

        Args:
            text: Raw input text
            language: Language code ("km" or "en")
            source: Source of the input
            ocr_confidence: Optional OCR confidence if from OCR

        Returns:
            Fully constructed MathProblem

        Raises:
            MathProcessingError: If problem cannot be built
        """
        # Create base problem
        if source == ProblemSource.OCR and ocr_confidence is not None:
            problem = MathProblem.from_ocr_result(
                text=text,
                language=language,
                ocr_confidence=ocr_confidence,
            )
        else:
            problem = MathProblem.from_manual_input(
                text=text,
                language=language,
            )
            problem.source = source

        # Stage 1: Normalize text
        is_from_ocr = source == ProblemSource.OCR
        normalization_result = normalize_text(text, is_from_ocr=is_from_ocr)
        problem.normalization = normalization_result

        if not normalization_result.normalized_text:
            problem.add_warning("Normalization produced empty result")
            problem.parsing_confidence = 0.0
            problem.update_confidence()
            raise MathProcessingError(
                "Text normalization failed: no mathematical content detected",
                details=problem.to_dict(),
            )

        # Stage 2: Detect intent
        try:
            intent = self.intent_classifier.classify(normalization_result.normalized_text)
            problem.detected_intent = intent.value
        except Exception as e:
            problem.add_warning(f"Intent detection failed: {e}")

        # Stage 3: Extract mathematical expression
        try:
            expression = extract_expression(normalization_result.normalized_text)
            if not expression:
                problem.add_warning("No mathematical expression found in text")
                problem.parsing_confidence = 0.5
                # Try using the normalized text directly as fallback
                expression = normalization_result.normalized_text
        except Exception as e:
            problem.add_warning(f"Expression extraction failed: {e}")
            expression = normalization_result.normalized_text

        problem.expression = expression

        # Stage 4: Parse to SymPy
        try:
            parsed = parse_math_text(expression)
            problem.sympy_expr = parsed.sympy_expr
            problem.variables = parsed.symbols
            problem.parsing_confidence = 1.0
        except ExpressionParseError as e:
            problem.add_warning(f"Math parsing failed: {e}")
            problem.parsing_confidence = 0.0
            problem.update_confidence()
            raise MathProcessingError(
                f"Failed to parse mathematical expression: {e}", details=problem.to_dict()
            )
        except Exception as e:
            problem.add_warning(f"Unexpected parsing error: {e}")
            problem.parsing_confidence = 0.0
            problem.update_confidence()
            raise MathProcessingError(
                f"Unexpected error during parsing: {e}", details=problem.to_dict()
            )

        # Stage 5: Classify problem type and detect characteristics
        try:
            problem_type, characteristics = classify_with_characteristics(parsed)
            problem.problem_type = problem_type
            problem.characteristics = characteristics
            problem.classification_confidence = 1.0
        except Exception as e:
            problem.add_warning(f"Classification failed: {e}")
            problem.classification_confidence = 0.5
            # Try basic classification as fallback
            try:
                from app.classifier.problem_classifier.classifier import classify_problem

                problem.problem_type = classify_problem(parsed)
            except Exception:
                problem.problem_type = "unknown"

        # Stage 6: Update overall confidence
        problem.update_confidence()

        return problem

    def build_batch(
        self,
        texts: list[str],
        language: str = "km",
        source: ProblemSource = ProblemSource.MANUAL,
        ocr_confidences: list[float] | None = None,
    ) -> list[MathProblem]:
        """
        Build multiple problems efficiently.

        Args:
            texts: List of raw input texts
            language: Language code
            source: Source of inputs
            ocr_confidences: Optional OCR confidences (must match texts length)

        Returns:
            List of MathProblem objects (may include errors)
        """
        problems = []

        for i, text in enumerate(texts):
            ocr_conf = None
            if ocr_confidences and i < len(ocr_confidences):
                ocr_conf = ocr_confidences[i]

            try:
                problem = self.build_from_text(
                    text=text,
                    language=language,
                    source=source,
                    ocr_confidence=ocr_conf,
                )
                problems.append(problem)
            except MathProcessingError as e:
                # Create a problem object with error state
                if source == ProblemSource.OCR and ocr_conf is not None:
                    problem = MathProblem.from_ocr_result(
                        text=text,
                        language=language,
                        ocr_confidence=ocr_conf,
                    )
                else:
                    problem = MathProblem.from_manual_input(text=text, language=language)

                problem.add_warning(f"Build failed: {e}")
                problem.overall_confidence = 0.0
                problem.metadata["error"] = str(e)
                problems.append(problem)

        return problems


# Singleton instance
_default_builder: ProblemBuilder | None = None


def get_problem_builder() -> ProblemBuilder:
    """Get singleton problem builder instance."""
    global _default_builder
    if _default_builder is None:
        _default_builder = ProblemBuilder()
    return _default_builder


def build_problem(
    text: str,
    language: str = "km",
    source: ProblemSource = ProblemSource.MANUAL,
    ocr_confidence: float | None = None,
) -> MathProblem:
    """
    Convenience function to build a problem with default builder.

    Args:
        text: Raw input text
        language: Language code ("km" or "en")
        source: Source of the input
        ocr_confidence: Optional OCR confidence

    Returns:
        Fully constructed MathProblem
    """
    builder = get_problem_builder()
    return builder.build_from_text(
        text=text,
        language=language,
        source=source,
        ocr_confidence=ocr_confidence,
    )
