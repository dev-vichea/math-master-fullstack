"""
Exercise service for processing complete math worksheets.

Orchestrates the full pipeline:
OCR → Layout Analysis → Instruction Detection → Problem Extraction →
Context-Aware Classification → Problem Solving → Exercise Document
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.classifier.context_aware_classifier import ContextAwareClassifier
from app.models.document import (
    BoundingBox,
    Exercise,
    Instruction,
    InstructionType,
    Problem,
    Section,
)
from app.models.problem import MathProblem, ProblemSource
from app.ocr.layout import ReadingOrderAnalyzer, RegionClassifier, RegionType, SpatialClusterer
from app.ocr.layout.reading_order import TextBlock
from app.parser.instruction_parser import InstructionDetector
from app.parser.math_parser.expression_parser import parse_math_text
from app.parser.problem_extractor import ProblemExtractor


@dataclass
class ProcessingResult:
    """Result of exercise processing."""

    exercise: Exercise
    success: bool
    errors: list[str]
    warnings: list[str]


class ExerciseService:
    """
    Service for processing complete exercise documents.

    Coordinates all components to transform raw OCR output into
    structured Exercise documents with solved problems.
    """

    def __init__(self):
        """Initialize exercise service with all required components."""
        self.reading_order_analyzer = ReadingOrderAnalyzer()
        self.region_classifier = RegionClassifier()
        self.spatial_clusterer = SpatialClusterer()
        self.instruction_detector = InstructionDetector()
        self.problem_extractor = ProblemExtractor()
        self.context_classifier = ContextAwareClassifier()

    def process_text(
        self,
        text: str,
        language: str = "km",
    ) -> ProcessingResult:
        """
        Process plain text exercise (no spatial information).

        Args:
            text: Exercise text with instructions and problems
            language: Language code ("km" or "en")

        Returns:
            ProcessingResult with structured exercise
        """
        lines = text.strip().split("\n")
        blocks = []

        # Create simple text blocks without spatial info
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            blocks.append(
                TextBlock(
                    text=line,
                    bounding_box=BoundingBox(
                        x=0.1,
                        y=0.1 + i * 0.05,  # Simple vertical spacing
                        width=0.8,
                        height=0.04,
                    ),
                    confidence=1.0,
                )
            )

        return self.process_blocks(blocks, language=language)

    def process_blocks(
        self,
        blocks: list[TextBlock],
        language: str = "km",
    ) -> ProcessingResult:
        """
        Process text blocks with spatial information.

        Args:
            blocks: Text blocks from OCR
            language: Language code

        Returns:
            ProcessingResult with structured exercise
        """
        errors = []
        warnings = []

        try:
            # Step 1: Analyze reading order
            self.reading_order_analyzer.analyze(blocks)

            # Step 2: Classify regions
            region_types = {}
            for block in blocks:
                region_type = self.region_classifier.classify(block)
                region_types[block] = region_type

            # Step 3: Extract sections (instruction + problems)
            sections = self._extract_sections(blocks, region_types, language)

            # Step 4: Build exercise document
            exercise = Exercise(language=language)

            for section in sections:
                exercise.add_section(section)

            # Check for warnings
            if exercise.get_total_problems() == 0:
                warnings.append("No problems detected in the document")

            if not any(s.instruction for s in sections):
                warnings.append("No instructions detected")

            return ProcessingResult(
                exercise=exercise,
                success=True,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(f"Processing failed: {str(e)}")
            return ProcessingResult(
                exercise=Exercise(language=language),
                success=False,
                errors=errors,
                warnings=warnings,
            )

    def _extract_sections(
        self,
        blocks: list[TextBlock],
        region_types: dict[TextBlock, RegionType],
        language: str,
    ) -> list[Section]:
        """
        Extract sections (instruction + problems) from blocks.

        Args:
            blocks: Ordered text blocks
            region_types: Region type for each block
            language: Language code

        Returns:
            List of Section objects
        """
        sections = []
        current_instruction: Instruction | None = None
        current_problems: list[Problem] = []
        current_context_text: str | None = None
        current_given_variables: dict[str, str] = {}

        for block in blocks:
            # First check if block text is a given context line (e.g. គេឲ្យ x = ..., y = ...)
            ctx_text, vars_dict = self._parse_given_context(block.text)
            if ctx_text and vars_dict:
                current_context_text = ctx_text
                current_given_variables.update(vars_dict)
                if not current_instruction:
                    current_instruction = Instruction(
                        text=f"គេឲ្យ {ctx_text}",
                        language=language,
                        instruction_type=InstructionType.EVALUATE,
                        bounding_box=block.bounding_box,
                        confidence=1.0,
                    )
                continue

            region_type = region_types.get(block, RegionType.UNKNOWN)

            # If classified as instruction, check if it actually contains problem items
            # (e.g. "ក. គណនា A = x+y" or "- ខ. គណនា C = x^2 - xy + y^2")
            # Do NOT convert if it is a numbered section instruction like "3. ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលលីនេអ៊ែរលំដាប់ទី1"
            if region_type == RegionType.INSTRUCTION:
                clean_txt = block.text.strip()
                is_section_heading = bool(
                    re.match(r"^(\d+|[ivxIVX]+|[០១២៣៤៥៦៧៨៩]+)[\.:\)]\s*(?:ដោះស្រាយ|គណនា|ចូរ|រក|បង្ហាញ|សង្ខេប|solve|find|calculate|evaluate|determine|prove)", clean_txt, re.IGNORECASE)
                    or any(k in clean_txt for k in ("សមីការឌីផេរ៉ង់ស្យែល", "differential equation", "លំដាប់ទី"))
                )
                if not is_section_heading:
                    extracted_probe = self.problem_extractor.extract_from_blocks(
                        [block], language=language
                    )
                    if extracted_probe and any(
                        self.region_classifier._math_pattern.search(p.content)
                        for p in extracted_probe
                    ):
                        region_type = RegionType.PROBLEM_CONTENT

            # Detect instructions
            if region_type == RegionType.INSTRUCTION:
                # Save previous section if exists
                if current_instruction and current_problems:
                    section = Section(
                        instruction=current_instruction,
                        problems=current_problems,
                        context_text=current_context_text,
                        given_variables=current_given_variables,
                    )
                    sections.append(section)
                    current_problems = []

                # Parse new instruction
                parsed_instruction = self.instruction_detector.detect(
                    block.text, language=language
                )
                if parsed_instruction:
                    current_instruction = parsed_instruction.to_instruction()
                    current_instruction.bounding_box = block.bounding_box
                else:
                    current_instruction = Instruction(
                        text=block.text,
                        language=language,
                        instruction_type=current_instruction.instruction_type
                        if current_instruction
                        else InstructionType.UNKNOWN,
                        bounding_box=block.bounding_box,
                    )

            # Detect problems
            elif region_type in (RegionType.PROBLEM_LABEL, RegionType.PROBLEM_CONTENT, RegionType.UNKNOWN, RegionType.HEADER):
                # Try to extract problem
                extracted = self.problem_extractor.extract_from_blocks(
                    [block], language=language
                )

                if extracted:
                    for ext_problem in extracted:
                        subproblems = self._split_subproblems(
                            label=ext_problem.label,
                            content=ext_problem.content,
                            label_type=ext_problem.label_type,
                        )

                        for sub_label, sub_content, sub_type in subproblems:
                            # Create MathProblem
                            math_problem = MathProblem(
                                source=ProblemSource.OCR,
                                language=language,
                                raw_input=sub_content,
                                expression=sub_content,
                                ocr_confidence=ext_problem.confidence,
                            )

                            # Try to parse and classify with context
                            try:
                                parsed = parse_math_text(sub_content)
                                math_problem.sympy_expr = parsed.sympy_expr
                                math_problem.variables = parsed.symbols

                                classification = self.context_classifier.classify(
                                    parsed, instruction=current_instruction
                                )
                                math_problem.problem_type = classification.problem_type
                                math_problem.classification_confidence = (
                                    classification.confidence
                                )
                                math_problem.characteristics = classification.characteristics

                            except Exception:
                                pass

                            # Build relationships
                            rels = []
                            if current_context_text:
                                rels.append(f"អាស្រ័យលើតម្លៃដែលបានផ្ដល់ (Depends on given values): {current_context_text}")

                            problem = Problem(
                                problem=math_problem,
                                label=sub_label,
                                label_type=sub_type,
                                bounding_box=ext_problem.bounding_box,
                                instruction_context=current_instruction,
                                context=dict(current_given_variables),
                                relationships=rels,
                            )

                            current_problems.append(problem)

        # Add final section
        if current_instruction and current_problems:
            section = Section(
                instruction=current_instruction,
                problems=current_problems,
                context_text=current_context_text,
                given_variables=current_given_variables,
            )
            sections.append(section)
        elif current_problems:
            default_instruction = Instruction(
                text="Problems",
                language=language,
                instruction_type=InstructionType.UNKNOWN,
            )
            section = Section(
                instruction=default_instruction,
                problems=current_problems,
                context_text=current_context_text,
                given_variables=current_given_variables,
            )
            sections.append(section)

        return sections

    def _parse_given_context(self, text: str) -> tuple[str | None, dict[str, str]]:
        """Detect and parse given shared context such as គេឲ្យ x = ..., y = ..."""
        import re

        norm = re.sub(r"==+", "=", text)
        norm = re.sub(r"(?<![a-zA-Z])v\^?(\d+)", r"\\sqrt{\1}", norm)
        is_ctx = bool(re.search(r"(?:គេឲ្យ|គេមាន|ប្រាប់ថា|given\s+that|given|let)", norm, re.I))
        if not is_ctx:
            # Check if line is purely variable assignments like x = ..., y = ...
            if re.search(r"^[a-zA-Z]\s*=\s*[^=]+(?:,\s*[a-zA-Z]\s*=\s*[^=]+)*$", norm.strip()):
                is_ctx = True

        if is_ctx:
            clean_ctx = re.sub(
                r"^\s*(?:\d+[\.)]|\([0-9a-zA-Z]+\))?\s*(?:គេឲ្យ|គេមាន|ប្រាប់ថា|given\s+that|given|let)\s*",
                "",
                norm,
                flags=re.I,
            ).strip()
            parts = re.split(r"(?:និង|នង|,|;)\s*", clean_ctx)
            vars_dict = {}
            for p in parts:
                p = p.strip(" ៚.,")
                m = re.match(r"^([a-zA-Z])\s*=\s*(.+)$", p)
                if m:
                    vars_dict[m.group(1)] = m.group(2).strip()
            if vars_dict:
                return clean_ctx, vars_dict
        return None, {}

    def _split_subproblems(
        self, label: str, content: str, label_type: ProblemLabel
    ) -> list[tuple[str, str, ProblemLabel]]:
        """Split a problem content if it contains multiple subproblems joined by Khmer and/comma."""
        import re

        clean = content.strip(" ៚.,")
        # Strip inline instruction verb at start of problem content (e.g. គណនា A = ...)
        m_inst = re.match(
            r"^(?:គណនា|រក|ដោះស្រាយ|សម្រួល|ពន្លា|ដាក់ជាផលគុណកត្តា|calculate|solve|simplify|find)\s*",
            clean,
            re.I,
        )
        if m_inst:
            clean = clean[m_inst.end():].strip()

        # Check for multiple expressions joined by and / និង / នង
        parts = re.split(r"\s*(?:និង|នង|\band\b)\s*", clean)
        if len(parts) > 1:
            res = []
            for i, p in enumerate(parts):
                p = p.strip(" ៚.,")
                if p:
                    sub_l = f"{label[:-1]}.{i+1}" if label.endswith(".") else f"{label}.{i+1}"
                    res.append((sub_l, p, label_type))
            if res:
                return res

        return [(label, clean, label_type)]

    def validate_exercise(self, exercise: Exercise) -> tuple[bool, list[str]]:
        """
        Validate exercise structure and content.

        Args:
            exercise: Exercise to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check basic structure
        if exercise.get_section_count() == 0:
            errors.append("Exercise has no sections")

        if exercise.get_total_problems() == 0:
            errors.append("Exercise has no problems")

        # Check each section
        for i, section in enumerate(exercise.sections):
            if not section.instruction:
                errors.append(f"Section {i} has no instruction")

            if section.get_problem_count() == 0:
                errors.append(f"Section {i} has no problems")

            # Validate problem sequences
            if section.problems:
                extractor = ProblemExtractor()
                extracted_list = []
                for problem in section.problems:
                    # Create ExtractedProblem for validation
                    from app.parser.problem_extractor.problem_extractor import (
                        ExtractedProblem,
                    )

                    ext = ExtractedProblem(
                        label=problem.label or "",
                        label_type=problem.label_type,
                        content=problem.problem.raw_input,
                        full_text=problem.problem.raw_input,
                    )
                    extracted_list.append(ext)

                if extracted_list:
                    is_valid, error = extractor.validate_sequence(extracted_list)
                    if not is_valid:
                        errors.append(f"Section {i}: {error}")

        return len(errors) == 0, errors

    def get_statistics(self, exercise: Exercise) -> dict:
        """
        Get statistics about the exercise.

        Args:
            exercise: Exercise to analyze

        Returns:
            Dictionary with statistics
        """
        stats = {
            "sections": exercise.get_section_count(),
            "total_problems": exercise.get_total_problems(),
            "problems_per_section": [],
            "instruction_types": [],
            "problem_types": {},
            "average_confidence": exercise.get_average_confidence(),
            "languages": set(),
        }

        for section in exercise.sections:
            stats["problems_per_section"].append(section.get_problem_count())
            stats["instruction_types"].append(section.instruction.instruction_type.value)
            stats["languages"].add(section.instruction.language)

            for problem in section.problems:
                problem_type = problem.problem.problem_type or "unknown"
                stats["problem_types"][problem_type] = (
                    stats["problem_types"].get(problem_type, 0) + 1
                )

        stats["languages"] = list(stats["languages"])

        return stats
