"""
Structured problem representation layer.

This module defines the intermediate representation between raw input (OCR/typed)
and the solver. It tracks:
- Problem source (OCR vs manual)
- Confidence scores at each stage
- Normalization transformations
- Detected problem characteristics

The MathProblem class is the unified format that flows through:
Input → Normalization → Classification → Solving → Verification → Explanation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sympy import Expr, Symbol
from sympy.core.relational import Relational


class ProblemSource(str, Enum):
    """Source of the mathematical problem."""

    MANUAL = "manual"  # User typed directly
    OCR = "ocr"  # Extracted from image via OCR
    IMPORTED = "imported"  # Imported from file/API
    UNKNOWN = "unknown"


class NormalizationStep(str, Enum):
    """Stages of text normalization applied."""

    KHMER_DIGITS = "khmer_digits"  # ០-៩ → 0-9
    KHMER_PUNCTUATION = "khmer_punctuation"  # Chan marks, etc.
    UNICODE_SUPERSCRIPTS = "unicode_superscripts"  # x² → x^2
    OPERATOR_STANDARDIZATION = "operator_standardization"  # × → *, ÷ → /
    OCR_ERROR_CORRECTION = "ocr_error_correction"  # O→0, l→1, etc.
    LATEX_NORMALIZATION = "latex_normalization"  # \frac{a}{b} → (a)/(b)
    WHITESPACE_CLEANUP = "whitespace_cleanup"  # Remove extra spaces
    PERCENTAGE_CONVERSION = "percentage_conversion"  # 50% → 0.5


@dataclass
class NormalizationResult:
    """Result of text normalization with tracking."""

    original_text: str
    normalized_text: str
    steps_applied: list[NormalizationStep]
    transformations: dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0  # 0.0 to 1.0
    warnings: list[str] = field(default_factory=list)

    def add_transformation(self, step: NormalizationStep, before: str, after: str) -> None:
        """Record a transformation that was applied."""
        self.steps_applied.append(step)
        self.transformations[f"{step.value}_{len(self.transformations)}"] = f"{before} → {after}"

    def add_warning(self, message: str) -> None:
        """Add a warning about potential ambiguity or low confidence."""
        self.warnings.append(message)
        # Reduce confidence for each warning
        self.confidence = max(0.1, self.confidence - 0.1)


@dataclass
class ProblemCharacteristics:
    """Detected characteristics of the mathematical problem."""

    has_equation: bool = False
    has_inequality: bool = False
    has_system: bool = False  # Multiple equations
    has_fractions: bool = False
    has_exponents: bool = False
    has_radicals: bool = False
    has_trigonometry: bool = False
    has_calculus: bool = False
    has_absolute_value: bool = False
    has_complex_numbers: bool = False

    variable_count: int = 0
    equation_count: int = 0
    max_polynomial_degree: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "has_equation": self.has_equation,
            "has_inequality": self.has_inequality,
            "has_system": self.has_system,
            "has_fractions": self.has_fractions,
            "has_exponents": self.has_exponents,
            "has_radicals": self.has_radicals,
            "has_trigonometry": self.has_trigonometry,
            "has_calculus": self.has_calculus,
            "has_absolute_value": self.has_absolute_value,
            "has_complex_numbers": self.has_complex_numbers,
            "variable_count": self.variable_count,
            "equation_count": self.equation_count,
            "max_polynomial_degree": self.max_polynomial_degree,
        }


@dataclass
class MathProblem:
    """
    Unified representation of a mathematical problem.

    This is the central data structure that flows through the entire pipeline:
    1. Created from raw input (OCR or typed text)
    2. Enriched with normalization metadata
    3. Analyzed for problem characteristics
    4. Classified into problem type
    5. Solved with step-by-step reasoning
    6. Verified
    7. Explained in target language
    """

    # Input metadata
    source: ProblemSource
    language: str  # "km" or "en"
    raw_input: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Normalization
    normalization: NormalizationResult | None = None

    # Mathematical representation
    expression: str | None = None  # Normalized math expression
    sympy_expr: Expr | Relational | None = None  # Parsed SymPy object
    variables: list[Symbol] = field(default_factory=list)

    # Problem analysis
    characteristics: ProblemCharacteristics = field(default_factory=ProblemCharacteristics)
    problem_type: str | None = None  # linear_equation, quadratic_equation, etc.
    detected_intent: str | None = None  # solve, evaluate, simplify, etc.

    # Confidence tracking
    ocr_confidence: float | None = None  # From OCR engine
    parsing_confidence: float = 1.0  # Did parsing succeed cleanly?
    classification_confidence: float = 1.0  # How confident is the classification?
    overall_confidence: float = 1.0  # Combined confidence score

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def update_confidence(self) -> None:
        """
        Recalculate overall confidence based on all pipeline stages.

        Overall confidence is the minimum of all stage confidences,
        since the weakest link determines reliability.
        """
        confidences = [self.parsing_confidence, self.classification_confidence]

        if self.ocr_confidence is not None:
            confidences.append(self.ocr_confidence)

        if self.normalization:
            confidences.append(self.normalization.confidence)

        self.overall_confidence = min(confidences) if confidences else 1.0

    def add_warning(self, message: str) -> None:
        """Add a warning and reduce confidence slightly."""
        self.warnings.append(message)
        self.overall_confidence = max(0.1, self.overall_confidence - 0.05)

    def is_reliable(self, threshold: float = 0.7) -> bool:
        """Check if the problem meets reliability threshold for solving."""
        return self.overall_confidence >= threshold

    def requires_review(self, threshold: float = 0.5) -> bool:
        """Check if problem should be reviewed by user before solving."""
        return self.overall_confidence < threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "source": self.source.value,
            "language": self.language,
            "raw_input": self.raw_input,
            "expression": self.expression,
            "variables": [str(v) for v in self.variables],
            "problem_type": self.problem_type,
            "detected_intent": self.detected_intent,
            "characteristics": self.characteristics.to_dict(),
            "confidence": {
                "overall": round(self.overall_confidence, 3),
                "ocr": round(self.ocr_confidence, 3) if self.ocr_confidence else None,
                "parsing": round(self.parsing_confidence, 3),
                "classification": round(self.classification_confidence, 3),
            },
            "warnings": self.warnings,
        }

        if self.normalization:
            result["normalization"] = {
                "original": self.normalization.original_text,
                "normalized": self.normalization.normalized_text,
                "steps_applied": [step.value for step in self.normalization.steps_applied],
                "confidence": round(self.normalization.confidence, 3),
                "warnings": self.normalization.warnings,
            }

        result.update(self.metadata)

        return result

    @classmethod
    def from_manual_input(
        cls,
        text: str,
        language: str = "km",
    ) -> MathProblem:
        """Create a MathProblem from manually typed text."""
        return cls(
            source=ProblemSource.MANUAL,
            language=language,
            raw_input=text,
            parsing_confidence=1.0,
            classification_confidence=1.0,
        )

    @classmethod
    def from_ocr_result(
        cls,
        text: str,
        language: str,
        ocr_confidence: float,
        ocr_metadata: dict[str, Any] | None = None,
    ) -> MathProblem:
        """Create a MathProblem from OCR-extracted text."""
        problem = cls(
            source=ProblemSource.OCR,
            language=language,
            raw_input=text,
            ocr_confidence=ocr_confidence,
        )

        if ocr_metadata:
            problem.metadata.update(ocr_metadata)

        # OCR results start with lower confidence
        if ocr_confidence < 0.9:
            problem.add_warning(f"OCR confidence is low ({ocr_confidence:.2f})")

        return problem


@dataclass
class MultiProblemSet:
    """
    Container for multiple related problems (e.g., from a single exercise sheet).

    Represents problems extracted from a single image/document that may contain
    multiple questions labeled a), b), c), etc.
    """

    exercise_title: str | None = None
    instruction: str | None = None
    problems: list[MathProblem] = field(default_factory=list)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_problem(self, problem: MathProblem) -> None:
        """Add a problem to the set."""
        self.problems.append(problem)

    def get_problem_count(self) -> int:
        """Get total number of problems in the set."""
        return len(self.problems)

    def get_average_confidence(self) -> float:
        """Calculate average confidence across all problems."""
        if not self.problems:
            return 0.0
        return sum(p.overall_confidence for p in self.problems) / len(self.problems)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "exercise_title": self.exercise_title,
            "instruction": self.instruction,
            "problem_count": self.get_problem_count(),
            "average_confidence": round(self.get_average_confidence(), 3),
            "problems": [p.to_dict() for p in self.problems],
            "source_metadata": self.source_metadata,
            "timestamp": self.timestamp.isoformat(),
        }
