"""
Problem extractor for detecting and extracting problems from text.

Identifies problem labels and their associated mathematical expressions,
building structured Problem objects with spatial information.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.document import BoundingBox, Problem, ProblemLabel
from app.models.problem import MathProblem, ProblemSource
from app.ocr.layout.reading_order import TextBlock


@dataclass
class ExtractedProblem:
    """Extracted problem with label and content."""

    label: str  # e.g., "a)", "ក.", "1."
    label_type: ProblemLabel
    content: str  # Mathematical expression/equation
    full_text: str  # Complete text including label
    bounding_box: BoundingBox | None = None
    confidence: float = 1.0


class ProblemExtractor:
    """
    Extract problems with labels from text.

    Detects various problem label formats:
    - Latin lowercase: a), b), c) or a., b., c.
    - Latin uppercase: A), B), C) or A., B., C.
    - Khmer: ក., ខ., គ., ឃ., ង., etc.
    - Numeric: 1), 2), 3) or 1., 2., 3.
    - Roman: i), ii), iii) or I), II), III)
    """

    # Khmer label characters (in order)
    KHMER_LABELS = [
        "ក",
        "ខ",
        "គ",
        "ឃ",
        "ង",
        "ច",
        "ឆ",
        "ជ",
        "ឈ",
        "ញ",
        "ដ",
        "ឋ",
        "ឌ",
        "ឍ",
        "ណ",
        "ត",
        "ថ",
        "ទ",
        "ធ",
        "ន",
        "ប",
        "ផ",
        "ព",
        "ភ",
        "ម",
        "យ",
        "រ",
        "ល",
        "វ",
        "ស",
        "ហ",
        "ឡ",
        "អ",
    ]

    # Latin lowercase labels
    LATIN_LOWER = list("abcdefghijklmnopqrstuvwxyz")

    # Latin uppercase labels
    LATIN_UPPER = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # Roman numerals (lowercase)
    ROMAN_LOWER = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]

    # Roman numerals (uppercase)
    ROMAN_UPPER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

    def __init__(self):
        """Initialize problem extractor."""
        # Compile regex patterns for efficiency
        self._patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict[ProblemLabel, re.Pattern]:
        """
        Compile regex patterns for different label types.
        
        Order matters! Roman numerals must be checked before single Latin letters.
        """
        # Use list of tuples to preserve order
        patterns = []

        # Khmer: ក. or ក។ or ក)
        khmer_chars = "|".join(self.KHMER_LABELS)
        patterns.append((ProblemLabel.KHMER, re.compile(rf"^({khmer_chars})[\.។)]")))

        # Numeric: 1) or 1.
        patterns.append((ProblemLabel.NUMERIC, re.compile(r"^(\d+)[\.)]")))

        # Roman uppercase: I) or I. (must come before Latin uppercase)
        patterns.append((ProblemLabel.ROMAN_UPPER, re.compile(r"^([IVX]+)[\.)]")))

        # Roman lowercase: i) or i. (must come before Latin lowercase)
        patterns.append((ProblemLabel.ROMAN_LOWER, re.compile(r"^([ivx]+)[\.)]")))

        # Latin uppercase: A) or A.
        patterns.append((ProblemLabel.LATIN_UPPER, re.compile(r"^([A-Z])[\.)]")))

        # Latin lowercase: a) or a.
        patterns.append((ProblemLabel.LATIN_LOWER, re.compile(r"^([a-z])[\.)]")))

        return patterns

    def extract_from_text(self, text: str, language: str = "km") -> list[ExtractedProblem]:
        """
        Extract problems from plain text.

        Args:
            text: Text containing problems
            language: Language hint ("km" or "en")

        Returns:
            List of extracted problems
        """
        lines = text.split("\n")
        problems = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to match problem label
            extracted = self._extract_from_line(line, language)
            if extracted:
                problems.append(extracted)

        return problems

    def extract_from_blocks(
        self,
        blocks: list[TextBlock],
        language: str = "km",
    ) -> list[ExtractedProblem]:
        """
        Extract problems from text blocks with spatial information.

        Args:
            blocks: Text blocks in reading order
            language: Language hint

        Returns:
            List of extracted problems with spatial info
        """
        problems = []

        for block in blocks:
            text = block.text.strip()
            if not text:
                continue

            # Try to extract problems (supports multi-column lines)
            extracted_list = self._extract_all_from_line(text, language)
            for extracted in extracted_list:
                extracted.bounding_box = block.bounding_box
                extracted.confidence = block.confidence
                problems.append(extracted)

        return problems

    def _extract_from_line(self, line: str, language: str) -> ExtractedProblem | None:
        """
        Extract problem from a single line of text.
        """
        results = self._extract_all_from_line(line, language)
        return results[0] if results else None

    def _extract_all_from_line(self, line: str, language: str) -> list[ExtractedProblem]:
        """
        Extract one or more problems from a line of text (supports multi-column layouts).
        """
        line = line.strip()
        # Clean leading noise characters from OCR like . - * •
        clean_start = re.sub(r"^[\s\-.*•·—_]+", "", line).strip()
        if not clean_start:
            return []

        # Find all label positions in line
        found = []
        for label_type, pattern in self._patterns:
            # Look for pattern at beginning of line
            m_start = pattern.match(clean_start)
            if m_start:
                lbl = m_start.group(0)
                found.append((0, len(lbl), lbl, label_type))

            # Also search for inline labels (multi-column: separated by spaces or dots)
            search_pat = re.compile(rf"(?<=[\s.…·_])({pattern.pattern.lstrip('^')})")
            for m in search_pat.finditer(clean_start):
                lbl = m.group(1)
                found.append((m.start(1), m.end(1), lbl, label_type))

        if not found:
            return []

        # Sort and deduplicate overlaps
        found.sort(key=lambda x: x[0])
        unique = []
        for item in found:
            if not unique or item[0] >= unique[-1][1]:
                unique.append(item)

        results = []
        for i, (s_idx, e_idx, lbl, l_type) in enumerate(unique):
            next_start = unique[i + 1][0] if i + 1 < len(unique) else len(clean_start)
            content = clean_start[e_idx:next_start].strip(" .…\t\r\n\u17d4\u17d5")
            if content:
                results.append(
                    ExtractedProblem(
                        label=lbl,
                        label_type=l_type,
                        content=content,
                        full_text=clean_start[s_idx:next_start].strip(),
                    )
                )

        return results

    def detect_label_type(self, text: str) -> ProblemLabel | None:
        """
        Detect the label type from text.

        Args:
            text: Text starting with a potential label

        Returns:
            ProblemLabel if detected, None otherwise
        """
        text = text.strip()
        for label_type, pattern in self._patterns:
            if pattern.match(text):
                return label_type
        return None

    def is_problem_line(self, text: str) -> bool:
        """
        Check if text line contains a problem label.

        Args:
            text: Text to check

        Returns:
            True if line starts with problem label
        """
        text = text.strip()
        for label_type, pattern in self._patterns:
            if pattern.match(text):
                return True
        return False

    def group_by_label_type(
        self,
        problems: list[ExtractedProblem],
    ) -> dict[ProblemLabel, list[ExtractedProblem]]:
        """
        Group problems by their label type.

        Args:
            problems: List of extracted problems

        Returns:
            Dictionary mapping label type to problems
        """
        groups: dict[ProblemLabel, list[ExtractedProblem]] = {}
        for problem in problems:
            if problem.label_type not in groups:
                groups[problem.label_type] = []
            groups[problem.label_type].append(problem)
        return groups

    def to_math_problems(
        self,
        problems: list[ExtractedProblem],
        language: str = "km",
        source: ProblemSource = ProblemSource.OCR,
    ) -> list[Problem]:
        """
        Convert extracted problems to Problem objects.

        Args:
            problems: List of extracted problems
            language: Language code
            source: Problem source

        Returns:
            List of Problem objects
        """
        result = []

        for i, extracted in enumerate(problems):
            # Create MathProblem
            math_problem = MathProblem(
                source=source,
                language=language,
                raw_input=extracted.content,
                expression=extracted.content,
                metadata={"label": extracted.label, "full_text": extracted.full_text},
            )

            # Set OCR confidence if available
            if source == ProblemSource.OCR:
                math_problem.ocr_confidence = extracted.confidence

            # Create Problem wrapper
            problem = Problem(
                problem=math_problem,
                label=extracted.label,
                label_type=extracted.label_type,
                bounding_box=extracted.bounding_box,
                reading_order=i,
            )

            result.append(problem)

        return result

    def extract_label_sequence(self, problems: list[ExtractedProblem]) -> list[str]:
        """
        Extract the sequence of labels from problems.

        Args:
            problems: List of problems

        Returns:
            List of label characters (e.g., ["a", "b", "c"])
        """
        labels = []
        for problem in problems:
            # Extract just the character from label
            for label_type, pattern in self._patterns:
                match = pattern.match(problem.label)
                if match:
                    labels.append(match.group(1))
                    break
        return labels

    def validate_sequence(self, problems: list[ExtractedProblem]) -> tuple[bool, str]:
        """
        Validate that problem labels form a valid sequence.

        Args:
            problems: List of problems to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not problems:
            return True, ""

        # Group by label type
        groups = self.group_by_label_type(problems)

        if len(groups) > 1:
            return False, "Mixed label types detected"

        label_type = list(groups.keys())[0]
        labels = self.extract_label_sequence(problems)

        # Get expected sequence based on label type
        if label_type == ProblemLabel.LATIN_LOWER:
            expected = self.LATIN_LOWER
        elif label_type == ProblemLabel.LATIN_UPPER:
            expected = self.LATIN_UPPER
        elif label_type == ProblemLabel.KHMER:
            expected = self.KHMER_LABELS
        elif label_type == ProblemLabel.NUMERIC:
            # Numeric should be 1, 2, 3, ...
            expected = [str(i) for i in range(1, len(labels) + 1)]
        elif label_type in (ProblemLabel.ROMAN_LOWER, ProblemLabel.ROMAN_UPPER):
            expected = self.ROMAN_LOWER if label_type == ProblemLabel.ROMAN_LOWER else self.ROMAN_UPPER
        else:
            return True, ""  # Unknown type, skip validation

        # Check if labels match expected sequence
        for i, (actual, exp) in enumerate(zip(labels, expected[: len(labels)])):
            if actual.lower() != exp.lower():
                return False, f"Expected '{exp}' at position {i}, got '{actual}'"

        return True, ""
