"""
Document structure models for exercise worksheets.

This module defines the hierarchical document structure for math exercise worksheets:
Exercise → Instruction → Section → Problem

The document models support:
- Complete worksheet understanding (not just individual formulas)
- Multiple instructions per page (e.g., "Solve" section then "Factor" section)
- Spatial layout tracking (coordinates, reading order)
- Context propagation (instruction → problems for classification)
- Multi-language support (Khmer, English)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.models.problem import MathProblem


class InstructionType(str, Enum):
    """Types of mathematical instructions."""

    SOLVE = "solve"  # ដោះស្រាយ - solve equation/system
    FACTOR = "factor"  # ដាក់ជាកត្តាកត់ - factor expression
    SIMPLIFY = "simplify"  # សង្រួត - simplify expression
    EXPAND = "expand"  # បង្ហាញ - expand expression
    EVALUATE = "evaluate"  # គណនា - calculate/evaluate
    FIND = "find"  # រកតម្លៃ - find value
    PROVE = "prove"  # បង្ហាញថា - prove/demonstrate
    COMPARE = "compare"  # ប្រៀបធៀប - compare expressions
    GRAPH = "graph"  # គូរក្រាប - draw graph
    DERIVATIVE = "derivative"  # គណនាដេរីវេ - calculate derivative
    INTEGRAL = "integral"  # គណនាអាំងតេក្រាល - calculate integral
    CONVERGENCE = "convergence"  # សិក្សាភាពរួម ឬរីក - study convergence/divergence
    SEQUENCE = "sequence"  # ស្វ៊ីត - sequence operations
    UNKNOWN = "unknown"  # Cannot determine instruction type



class ProblemLabel(str, Enum):
    """Label styles for sub-problems."""

    LATIN_LOWER = "latin_lower"  # a, b, c, d
    LATIN_UPPER = "latin_upper"  # A, B, C, D
    KHMER = "khmer"  # ក, ខ, គ, ឃ, ង
    NUMERIC = "numeric"  # 1, 2, 3, 4
    ROMAN_LOWER = "roman_lower"  # i, ii, iii, iv
    ROMAN_UPPER = "roman_upper"  # I, II, III, IV
    NONE = "none"  # No label


@dataclass
class BoundingBox:
    """Spatial coordinates for text regions."""

    x: float  # Left edge (0.0 to 1.0 normalized)
    y: float  # Top edge (0.0 to 1.0 normalized)
    width: float  # Width (0.0 to 1.0 normalized)
    height: float  # Height (0.0 to 1.0 normalized)
    page: int = 0  # Page number (0-indexed)

    def center_x(self) -> float:
        """Calculate center X coordinate."""
        return self.x + self.width / 2

    def center_y(self) -> float:
        """Calculate center Y coordinate."""
        return self.y + self.height / 2

    def area(self) -> float:
        """Calculate bounding box area."""
        return self.width * self.height

    def intersects(self, other: BoundingBox) -> bool:
        """Check if this box intersects with another."""
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "width": round(self.width, 4),
            "height": round(self.height, 4),
            "page": self.page,
        }


@dataclass
class Instruction:
    """
    Mathematical instruction for a group of problems.

    Examples:
    - "ចូរដាក់ជាកត្តាកត់នៃពហុធាខាងក្រោម" (Factor the following polynomials)
    - "ដោះស្រាយសមីការខាងក្រោម" (Solve the following equations)
    - "គណនាតម្លៃ" (Calculate the value)
    """

    text: str  # Original instruction text
    language: str  # "km" or "en"
    instruction_type: InstructionType
    bounding_box: BoundingBox | None = None
    confidence: float = 1.0  # Detection confidence

    # Parsing metadata
    detected_keywords: list[str] = field(default_factory=list)  # Matched keywords
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "text": self.text,
            "language": self.language,
            "type": self.instruction_type.value,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "confidence": round(self.confidence, 3),
            "detected_keywords": self.detected_keywords,
        }


@dataclass
class Problem:
    """
    Individual math problem within a section.

    Links together:
    - Spatial location (bounding box)
    - Problem label (a, b, c or ក, ខ, គ)
    - Actual math content (MathProblem)
    - Parent instruction context
    """

    problem: MathProblem  # The actual math problem
    label: str | None = None  # "a", "b", "c" or "ក", "ខ", "គ" or "1", "2"
    label_type: ProblemLabel = ProblemLabel.NONE
    bounding_box: BoundingBox | None = None
    reading_order: int = 0  # Position in reading order (0-indexed)

    # Context linking
    instruction_context: Instruction | None = None
    context: dict[str, str] = field(default_factory=dict)
    relationships: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "label": self.label,
            "label_type": self.label_type.value,
            "reading_order": self.reading_order,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "problem": self.problem.to_dict(),
            "context": self.context,
            "relationships": self.relationships,
        }

        if self.instruction_context:
            result["instruction_type"] = self.instruction_context.instruction_type.value

        return result


@dataclass
class Section:
    """
    Section of problems under a single instruction.

    Example:
    ចូរដាក់ជាកត្តាកត់  ← Instruction
    ក. x² - 4         ← Problem 1
    ខ. x² - 5x + 6    ← Problem 2
    គ. 2x² + 8x       ← Problem 3
    """

    instruction: Instruction
    problems: list[Problem] = field(default_factory=list)
    section_number: int = 0  # Section index in document (0-indexed)

    # Shared context and given values (e.g. គេឲ្យ x = 2 - \sqrt{3}, y = 3 + \sqrt{3})
    context_text: str | None = None
    given_variables: dict[str, str] = field(default_factory=dict)

    # Layout metadata
    bounding_box: BoundingBox | None = None  # Bounding box of entire section

    def add_problem(self, problem: Problem) -> None:
        """Add a problem to this section."""
        # Link problem to instruction context
        problem.instruction_context = self.instruction
        if self.given_variables and not problem.context:
            problem.context = dict(self.given_variables)
        self.problems.append(problem)

    def get_problem_count(self) -> int:
        """Get number of problems in section."""
        return len(self.problems)

    def get_average_confidence(self) -> float:
        """Calculate average confidence across all problems."""
        if not self.problems:
            return 0.0
        return sum(p.problem.overall_confidence for p in self.problems) / len(self.problems)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "section_number": self.section_number,
            "instruction": self.instruction.to_dict(),
            "context_text": self.context_text,
            "given_variables": self.given_variables,
            "problem_count": self.get_problem_count(),
            "average_confidence": round(self.get_average_confidence(), 3),
            "problems": [p.to_dict() for p in self.problems],
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
        }


@dataclass
class Exercise:
    """
    Complete exercise document (worksheet).

    Represents a full math worksheet that may contain:
    - Title/header
    - Multiple instructions
    - Multiple sections of problems
    - Metadata about the document

    Example structure:
    កិច្ចការផ្ទះលេខ ៥                    ← Title
    ចូរដាក់ជាកត្តាកត់                      ← Instruction 1
    ក. x² - 4                             ← Section 1, Problem 1
    ខ. x² - 5x + 6                        ← Section 1, Problem 2

    ដោះស្រាយសមីការ                        ← Instruction 2
    ក. 2x + 5 = 11                        ← Section 2, Problem 1
    ខ. x² - 3x - 4 = 0                    ← Section 2, Problem 2
    """

    sections: list[Section] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Document metadata
    title: str | None = None
    language: str = "km"  # Primary language
    page_count: int = 1

    # OCR metadata
    ocr_engine: str | None = None
    ocr_confidence: float | None = None
    image_metadata: dict[str, Any] = field(default_factory=dict)

    # Document structure detection
    detection_confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)

    def add_section(self, section: Section) -> None:
        """Add a section to the exercise."""
        section.section_number = len(self.sections)
        self.sections.append(section)

    def get_section_count(self) -> int:
        """Get number of sections in exercise."""
        return len(self.sections)

    def get_total_problems(self) -> int:
        """Get total number of problems across all sections."""
        return sum(section.get_problem_count() for section in self.sections)

    def get_all_problems(self) -> list[Problem]:
        """Get flattened list of all problems."""
        problems = []
        for section in self.sections:
            problems.extend(section.problems)
        return problems

    def get_average_confidence(self) -> float:
        """Calculate average confidence across all problems."""
        all_problems = self.get_all_problems()
        if not all_problems:
            return 0.0
        total = sum(p.problem.overall_confidence for p in all_problems)
        return total / len(all_problems)

    def add_warning(self, message: str) -> None:
        """Add a warning about document structure detection."""
        self.warnings.append(message)
        self.detection_confidence = max(0.1, self.detection_confidence - 0.1)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "title": self.title,
            "language": self.language,
            "page_count": self.page_count,
            "section_count": self.get_section_count(),
            "total_problems": self.get_total_problems(),
            "sections": [s.to_dict() for s in self.sections],
            "confidence": {
                "detection": round(self.detection_confidence, 3),
                "ocr": round(self.ocr_confidence, 3) if self.ocr_confidence else None,
                "average_problem": round(self.get_average_confidence(), 3),
            },
            "warnings": self.warnings,
            "ocr_engine": self.ocr_engine,
            "timestamp": self.timestamp.isoformat(),
        }
