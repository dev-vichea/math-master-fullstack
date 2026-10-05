"""
Exercise Document Parser - Build Document hierarchy from TextBlocks.

This parser enhances the existing exercise_parser.py to work with spatial
layout information. It builds the canonical Exercise → Section → Problem
hierarchy while preserving bounding boxes and reading order.

Key differences from exercise_parser.py:
- Accepts TextBlock[] with spatial coordinates (not flat text)
- Builds full Document hierarchy (Exercise/Section/Problem models)
- Preserves bounding boxes throughout
- Detects shared context/given variables
- Links instructions to problems spatially
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.classifier.problem_classifier.intent_classifier import (
    MathIntent,
    RuleBasedIntentClassifier,
)
from app.models.document import (
    BoundingBox,
    Exercise,
    Instruction,
    InstructionType,
    Problem,
    ProblemLabel,
    Section,
)
from app.models.problem import MathProblem, ProblemSource
from app.ocr.layout.reading_order import TextBlock
from app.ocr.layout.region_classifier import RegionType
from app.parser.exercise_parser.exercise_parser import (
    _HEADER_RE,
    _INSTRUCTION_RE,
    _SUBITEM_RE,
    _extract_single_math_expression,
    _is_valid_math_expression,
)

logger = logging.getLogger("app.parser.document_parser")

_intent_classifier = RuleBasedIntentClassifier()


class ExerciseDocumentParser:
    """
    Parser that builds Exercise → Section → Problem hierarchy from TextBlocks.
    
    This parser combines spatial layout information with text parsing to
    create a properly structured document with preserved bounding boxes.
    """

    def __init__(self):
        """Initialize the document parser."""
        self._instruction_type_map = self._build_instruction_type_map()

    def parse(
        self,
        text_blocks: list[TextBlock],
        region_classifications: dict[TextBlock, RegionType] | None = None,
    ) -> Exercise:
        """
        Parse text blocks into Exercise document structure.
        
        Args:
            text_blocks: List of text blocks with bounding boxes (in reading order)
            region_classifications: Optional mapping of blocks to region types
            
        Returns:
            Exercise with full hierarchy and spatial information
        """
        exercise = Exercise()
        region_map = region_classifications or {}

        if not text_blocks:
            exercise.add_warning("No text blocks to parse")
            return exercise

        # Group blocks by type
        header_blocks = []
        instruction_blocks = []
        context_blocks = []
        problem_blocks = []
        
        for block in text_blocks:
            region_type = region_map.get(block, RegionType.UNKNOWN)
            text = block.text.strip()
            
            if not text:
                continue
                
            if region_type == RegionType.HEADER or self._is_header(text):
                header_blocks.append(block)
            elif region_type == RegionType.INSTRUCTION or self._is_instruction(text):
                instruction_blocks.append(block)
            elif region_type == RegionType.PROBLEM_LABEL:
                # Labels are typically merged with their content
                problem_blocks.append(block)
            elif region_type == RegionType.PROBLEM_CONTENT:
                problem_blocks.append(block)
            elif region_type == RegionType.PROBLEM:
                problem_blocks.append(block)
            elif self._is_context(text):
                context_blocks.append(block)
            else:
                # Try to classify by content
                if _SUBITEM_RE.match(text):
                    problem_blocks.append(block)
                elif _is_valid_math_expression(text):
                    problem_blocks.append(block)

        # Extract title
        if header_blocks:
            exercise.title = header_blocks[0].text.strip()
            exercise.language = "km" if self._contains_khmer(exercise.title) else "en"

        # Build sections from instructions and problems
        if instruction_blocks or problem_blocks:
            sections = self._build_sections(
                instruction_blocks,
                context_blocks,
                problem_blocks,
            )
            for section in sections:
                exercise.add_section(section)

        # If no sections created but we have problem blocks, create default section
        if not exercise.sections and problem_blocks:
            default_section = self._create_default_section(problem_blocks)
            if default_section:
                exercise.add_section(default_section)

        logger.info(
            f"Parsed exercise: {exercise.get_section_count()} sections, "
            f"{exercise.get_total_problems()} problems"
        )

        return exercise

    def _build_sections(
        self,
        instruction_blocks: list[TextBlock],
        context_blocks: list[TextBlock],
        problem_blocks: list[TextBlock],
    ) -> list[Section]:
        """
        Build Section objects from instruction, context, and problem blocks.
        
        Sections are created based on instruction blocks. Problems are assigned
        to sections based on spatial proximity and reading order.
        """
        sections: list[Section] = []

        if not instruction_blocks:
            # No explicit instructions, create one section with all problems
            if problem_blocks:
                section = self._create_default_section(problem_blocks)
                if section:
                    sections.append(section)
            return sections

        # Create sections for each instruction
        for i, inst_block in enumerate(instruction_blocks):
            # Parse instruction
            instruction = self._parse_instruction(inst_block)
            
            # Determine which problems belong to this section
            # Use spatial reasoning: problems that come after this instruction
            # and before the next instruction
            next_inst_y = None
            if i + 1 < len(instruction_blocks):
                next_inst_y = instruction_blocks[i + 1].bounding_box.y
            
            section_problems = self._extract_section_problems(
                problem_blocks,
                after_y=inst_block.bounding_box.y,
                before_y=next_inst_y,
            )
            
            # Extract context/given variables
            section_context = self._extract_context(
                context_blocks,
                after_y=inst_block.bounding_box.y,
                before_y=section_problems[0].bounding_box.y if section_problems else None,
            )
            
            # Build section
            section = Section(
                instruction=instruction,
                context_text=section_context.get("text"),
                given_variables=section_context.get("variables", {}),
            )
            
            # Parse and add problems
            for prob_block in section_problems:
                problem = self._parse_problem(prob_block, instruction)
                if problem:
                    section.add_problem(problem)
            
            # Calculate section bounding box
            if section_problems:
                section.bounding_box = self._calculate_section_bbox(
                    inst_block,
                    section_problems,
                )
            
            sections.append(section)

        return sections

    def _parse_instruction(self, block: TextBlock) -> Instruction:
        """Parse a text block into an Instruction object."""
        text = block.text.strip()
        
        # Detect instruction type
        inst_type = self._classify_instruction_type(text)
        
        # Detect language
        language = "km" if self._contains_khmer(text) else "en"
        
        # Extract keywords that matched
        keywords = self._extract_matched_keywords(text)
        
        return Instruction(
            text=text,
            language=language,
            instruction_type=inst_type,
            bounding_box=block.bounding_box,
            confidence=block.confidence,
            detected_keywords=keywords,
        )

    def _parse_problem(
        self,
        block: TextBlock,
        instruction: Instruction | None = None,
    ) -> Problem | None:
        """Parse a text block into a Problem object."""
        text = block.text.strip()
        
        if not text:
            return None

        # Extract label if present
        label, label_type = self._extract_label(text)
        
        # Remove label from text to get math expression
        if label:
            text_without_label = re.sub(r"^\s*" + re.escape(label) + r"\s*", "", text)
        else:
            text_without_label = text
        
        # Extract math expression
        expression = _extract_single_math_expression(text_without_label)
        
        if not expression or not _is_valid_math_expression(expression):
            logger.debug(f"No valid math expression in block: {text[:50]}")
            return None

        # Create MathProblem
        math_problem = MathProblem(
            source=ProblemSource.OCR,
            language="km" if self._contains_khmer(text) else "en",
            raw_input=expression,
            ocr_confidence=block.confidence,
        )
        
        # Create Problem wrapper
        problem = Problem(
            problem=math_problem,
            label=label,
            label_type=label_type,
            bounding_box=block.bounding_box,
            instruction_context=instruction,
        )
        
        return problem

    def _extract_label(self, text: str) -> tuple[str | None, ProblemLabel]:
        """Extract problem label and determine its type."""
        match = _SUBITEM_RE.match(text)
        
        if not match:
            return None, ProblemLabel.NONE
        
        # Extract the captured label
        label_text = next((g for g in match.groups() if g is not None), None)
        
        if not label_text:
            return None, ProblemLabel.NONE
        
        # Determine label type
        if re.match(r"^[a-z]$", label_text):
            label_type = ProblemLabel.LATIN_LOWER
        elif re.match(r"^[A-Z]$", label_text):
            label_type = ProblemLabel.LATIN_UPPER
        elif re.match(r"^[\u1780-\u17a2]$", label_text):  # Khmer consonants
            label_type = ProblemLabel.KHMER
        elif re.match(r"^\d+$", label_text):
            label_type = ProblemLabel.NUMERIC
        elif re.match(r"^[ivx]+$", label_text.lower()):
            label_type = ProblemLabel.ROMAN_LOWER
        else:
            label_type = ProblemLabel.NONE
        
        return label_text, label_type

    def _extract_section_problems(
        self,
        problem_blocks: list[TextBlock],
        after_y: float,
        before_y: float | None,
    ) -> list[TextBlock]:
        """Extract problems that belong to a section based on Y coordinates."""
        section_blocks = []
        
        for block in problem_blocks:
            block_y = block.bounding_box.y
            
            # Must be after instruction
            if block_y <= after_y:
                continue
            
            # Must be before next instruction (if any)
            if before_y is not None and block_y >= before_y:
                continue
            
            section_blocks.append(block)
        
        return section_blocks

    def _extract_context(
        self,
        context_blocks: list[TextBlock],
        after_y: float | None,
        before_y: float | None,
    ) -> dict[str, Any]:
        """Extract context text and given variables."""
        result = {"text": None, "variables": {}}
        
        relevant_blocks = []
        for block in context_blocks:
            block_y = block.bounding_box.y
            
            if after_y is not None and block_y <= after_y:
                continue
            if before_y is not None and block_y >= before_y:
                continue
                
            relevant_blocks.append(block)
        
        if not relevant_blocks:
            return result
        
        # Combine text
        context_text = " ".join(b.text for b in relevant_blocks)
        result["text"] = context_text
        
        # Try to extract given variables (e.g., "គេឱ្យ x = 2", "Given x = 2")
        # Pattern: variable = expression
        var_pattern = r"([a-zA-Z])\s*=\s*([^,;\.]+)"
        matches = re.findall(var_pattern, context_text)
        
        for var_name, var_value in matches:
            result["variables"][var_name.strip()] = var_value.strip()
        
        return result

    def _calculate_section_bbox(
        self,
        inst_block: TextBlock,
        problem_blocks: list[TextBlock],
    ) -> BoundingBox:
        """Calculate bounding box encompassing entire section."""
        all_boxes = [inst_block.bounding_box] + [
            b.bounding_box for b in problem_blocks
        ]
        
        min_x = min(b.x for b in all_boxes)
        min_y = min(b.y for b in all_boxes)
        max_x = max(b.x + b.width for b in all_boxes)
        max_y = max(b.y + b.height for b in all_boxes)
        
        return BoundingBox(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
            page=inst_block.bounding_box.page,
        )

    def _create_default_section(
        self,
        problem_blocks: list[TextBlock],
    ) -> Section | None:
        """Create a default section when no instruction is present."""
        if not problem_blocks:
            return None
        
        # Create generic instruction
        instruction = Instruction(
            text="គណនា",  # Default: "Calculate"
            language="km",
            instruction_type=InstructionType.EVALUATE,
            confidence=0.5,  # Low confidence since it's inferred
        )
        
        section = Section(instruction=instruction)
        
        for prob_block in problem_blocks:
            problem = self._parse_problem(prob_block, instruction)
            if problem:
                section.add_problem(problem)
        
        return section

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _is_header(self, text: str) -> bool:
        """Check if text looks like a header."""
        return bool(_HEADER_RE.match(text))

    def _is_instruction(self, text: str) -> bool:
        """Check if text looks like an instruction."""
        return bool(_INSTRUCTION_RE.search(text))

    def _is_context(self, text: str) -> bool:
        """Check if text looks like context/given information."""
        # Look for "គេឱ្យ" (given), "given", "let", etc.
        context_patterns = [
            r"គេ(?:ឱ្យ|ឲ្យ)",  # Khmer "given"
            r"\bgiven\b",
            r"\blet\b",
            r"\bwhere\b",
            r"\bif\b.*=",
        ]
        
        for pattern in context_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def _contains_khmer(self, text: str) -> bool:
        """Check if text contains Khmer characters."""
        return bool(re.search(r"[\u1780-\u17ff]", text))

    def _classify_instruction_type(self, text: str) -> InstructionType:
        """Classify instruction text into InstructionType enum."""
        text_lower = text.lower()
        
        for inst_type, keywords in self._instruction_type_map.items():
            for keyword in keywords:
                if keyword in text or keyword in text_lower:
                    return inst_type
        
        return InstructionType.UNKNOWN

    def _build_instruction_type_map(self) -> dict[InstructionType, list[str]]:
        """Build mapping of instruction types to keywords."""
        return {
            InstructionType.SOLVE: [
                "ដោះស្រាយ", "solve", "find", "រក",
            ],
            InstructionType.FACTOR: [
                "ដាក់ជាកត្តាកត់", "ដាក់ជាផលគុណកត្តា", "factor", "factorise",
            ],
            InstructionType.SIMPLIFY: [
                "សម្រួល", "simplify", "សង្ខេប",
            ],
            InstructionType.EXPAND: [
                "បង្ហាញ", "ពន្លា", "expand",
            ],
            InstructionType.EVALUATE: [
                "គណនា", "calculate", "evaluate", "compute",
            ],
            InstructionType.FIND: [
                "រកតម្លៃ", "find value", "determine",
            ],
            InstructionType.PROVE: [
                "បង្ហាញថា", "ផ្ទៀងផ្ទាត់", "prove", "show that", "verify",
            ],
            InstructionType.INTEGRAL: [
                "អាំងតេក្រាល", "integral", "integrate",
            ],
            InstructionType.DERIVATIVE: [
                "ដេរីវេ", "derivative", "differentiate",
            ],
            InstructionType.CONVERGENCE: [
                "ភាពរួម", "convergence", "divergence",
            ],
            InstructionType.DIFFERENTIAL_EQUATION: [
                "ឌីផេរ៉ង់ស្យែល", "differential equation",
            ],
        }

    def _extract_matched_keywords(self, text: str) -> list[str]:
        """Extract keywords that matched for instruction classification."""
        matched = []
        text_lower = text.lower()
        
        for keywords in self._instruction_type_map.values():
            for keyword in keywords:
                if keyword in text or keyword in text_lower:
                    matched.append(keyword)
        
        return matched
