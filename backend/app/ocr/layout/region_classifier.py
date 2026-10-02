"""
Region classification for text blocks.

Classifies text blocks into semantic types: header, instruction, problem, label, etc.
Uses spatial and textual features for classification.
"""

from __future__ import annotations

import re
from enum import Enum

from app.ocr.layout.reading_order import TextBlock


class RegionType(str, Enum):
    """Types of text regions in a math exercise document."""

    HEADER = "header"  # Title, exercise name
    INSTRUCTION = "instruction"  # Mathematical instruction (solve, factor, etc.)
    PROBLEM_LABEL = "problem_label"  # a), b), c) or ក., ខ., គ.
    PROBLEM_CONTENT = "problem_content"  # Mathematical expression
    PROBLEM = "problem"  # Combined label + content
    FOOTER = "footer"  # Page number, footer text
    NOISE = "noise"  # Irrelevant text, artifacts
    UNKNOWN = "unknown"  # Cannot determine


class RegionClassifier:
    """
    Classify text blocks into semantic region types.

    Uses rule-based classification based on:
    - Text content patterns (keywords, mathematical notation)
    - Spatial features (position, size, alignment)
    - Context (previous blocks, layout structure)
    """

    # Khmer problem labels: ក, ខ, គ, ឃ, ង, ច, ឆ, ជ, ឈ, ញ
    KHMER_LABELS = "កខគឃងចឆជឈញដឋឌឍណតថទធនបផពភមយរលវសហឡអ"

    # Instruction keywords (Khmer)
    INSTRUCTION_KEYWORDS_KM = [
        "ចូរ",  # Please/Let's
        "ដោះស្រាយ",  # Solve
        "ដាក់ជាកត្តាកត់",  # Factor
        "កត្តាកត់",  # Factor
        "ដាក់កត្តា",  # Factor (shortened)
        "ដាក់ជាផលគុណកត្តា",  # Factor (product form)
        "ដាក់ជាផលគណកតា",  # Factor (OCR variation)
        "ផលគណកតា",  # Product factor (OCR variation)
        "គណនា",  # Calculate
        "រក",  # Find
        "សង្ខេប",  # Simplify
        "បង្ហាញ",  # Show/expand
        "ពន្លា",  # Expand
        "ប្រៀបធៀប",  # Compare
        "គូរ",  # Draw
        "បង្ហាញថា",  # Prove/show that
    ]

    # Instruction keywords (English)
    INSTRUCTION_KEYWORDS_EN = [
        "solve",
        "factor",
        "simplify",
        "expand",
        "calculate",
        "find",
        "evaluate",
        "compute",
        "determine",
        "prove",
        "show",
        "verify",
        "compare",
        "graph",
        "plot",
    ]

    def __init__(self):
        """Initialize region classifier."""
        # Compile regex patterns for efficiency
        self._label_pattern = self._compile_label_patterns()
        # Match math-like characters: variables, digits, operators
        # Explicitly list each Khmer digit to avoid Unicode range issues
        # Khmer digits: ០១២៣៤៥៦៧៨៩ (U+17E0-U+17E9)
        self._math_pattern = re.compile(r"[xyzXYZ០១២៣៤៥៦៧៨៩0-9+\-*/=^()[\]{}]")

    def _compile_label_patterns(self) -> re.Pattern:
        """Compile pattern for problem labels."""
        patterns = [
            r"^[a-zA-Z]\)",  # a), b), A), B)
            r"^[a-zA-Z]\.",  # a., b., A., B.
            r"^[{0}][។\.)]+".format(self.KHMER_LABELS),  # ក។, ខ.
            r"^\d+\)",  # 1), 2), 3)
            r"^\d+\.",  # 1., 2., 3.
            r"^[ivxIVX]+\)",  # i), ii), iii), IV), V)
            r"^[ivxIVX]+\.",  # i., ii., iii., IV., V.
        ]
        return re.compile("|".join(patterns))

    def classify(self, block: TextBlock, context: dict | None = None) -> RegionType:
        """
        Classify a text block into a region type.

        Args:
            block: Text block to classify
            context: Optional context information (previous blocks, page position, etc.)

        Returns:
            Classified region type
        """
        text = block.text.strip()

        if not text:
            return RegionType.NOISE

        # Check for problem labels
        if self._is_problem_label(text):
            return RegionType.PROBLEM_LABEL

        # Check for instructions
        if self._is_instruction(text):
            return RegionType.INSTRUCTION

        # Check for header (title, exercise name)
        if self._is_header(block, context):
            return RegionType.HEADER

        # Check for mathematical content
        if self._is_math_content(text):
            return RegionType.PROBLEM_CONTENT

        # Check for footer
        if self._is_footer(block, context):
            return RegionType.FOOTER

        return RegionType.UNKNOWN

    def _is_problem_label(self, text: str) -> bool:
        """Check if text is a problem label (a), b), ក., etc.)."""
        # Must be short
        if len(text) > 10:
            return False

        # Match label patterns
        return bool(self._label_pattern.match(text))

    def _is_instruction(self, text: str) -> bool:
        """Check if text is an instruction."""
        text_lower = text.lower()

        # Check for Khmer instruction keywords
        for keyword in self.INSTRUCTION_KEYWORDS_KM:
            if keyword in text:
                return True

        # Check for English instruction keywords
        for keyword in self.INSTRUCTION_KEYWORDS_EN:
            if keyword in text_lower:
                return True

        return False

    def _is_header(self, block: TextBlock, context: dict | None) -> bool:
        """Check if text is a header/title."""
        text = block.text.strip()

        # Headers are usually near the top
        if block.bounding_box.y > 0.3:  # Below 30% of page
            return False

        # Headers are typically short and may contain numbers (exercise number)
        if len(text) > 100:
            return False

        # Headers often contain keywords
        header_keywords = [
            "លំហាត់",  # Exercise (Khmer)
            "កិច្ចការ",  # Homework (Khmer)
            "exercise",
            "homework",
            "quiz",
            "test",
            "worksheet",
            "problem",
            "chapter",
        ]

        text_lower = text.lower()
        for keyword in header_keywords:
            if keyword in text_lower or keyword in text:
                return True

        return False

    def _is_math_content(self, text: str) -> bool:
        """Check if text contains mathematical content."""
        # Remove spaces for accurate counting
        text_no_space = text.replace(" ", "")
        
        if not text_no_space:
            return False

        # Count math-like characters
        math_char_list = [c for c in text_no_space if self._math_pattern.search(c)]
        math_chars = len(math_char_list)
        
        # Must have at least some math characters
        if math_chars < 2:
            return False

        # At least 40% of characters should be math-related
        # This prevents Khmer instruction text from being classified as math
        ratio = math_chars / len(text_no_space)
        return ratio >= 0.4

    def _is_footer(self, block: TextBlock, context: dict | None) -> bool:
        """Check if text is a footer (page number, etc.)."""
        text = block.text.strip()

        # Footers are usually near the bottom
        if block.bounding_box.y < 0.85:  # Above 85% of page
            return False

        # Footers are typically short
        if len(text) > 50:
            return False

        # Check for page number patterns
        page_patterns = [
            r"^\d+$",  # Just a number
            r"^page\s+\d+",  # "page 1", "page 2"
            r"^p\.\s*\d+",  # "p. 1", "p. 2"
            r"^\d+\s*/\s*\d+$",  # "1/5", "2/5"
            r"^ទំព័រ\s*\d+",  # "ទំព័រ ១" (page in Khmer)
        ]

        text_lower = text.lower()
        for pattern in page_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def extract_label(self, text: str) -> str | None:
        """
        Extract problem label from text.

        Args:
            text: Text containing a label

        Returns:
            Extracted label or None if no label found
        """
        match = self._label_pattern.match(text)
        if match:
            return match.group(0)
        return None
