"""
Knowledge Base Models for Lesson-Aware Mathematics Instruction.

Structure:
Chapter → Lesson → Concept → Rule/Formula → Method → Explanation Template → Examples
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SubjectDomain(str, Enum):
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    GEOMETRY = "geometry"
    TRIGONOMETRY = "trigonometry"
    STATISTICS = "statistics"


@dataclass
class ExplanationStepTemplate:
    """Defines what should be taught in a single step of a method."""

    order: int
    action_type: str  # e.g. "identify_common_factor", "extract_factor", "apply_rule", "simplify", "verify"
    title_km: str
    title_en: str
    rationale_template_km: str  # Why this step is being done
    rationale_template_en: str
    rule_reference: str | None = None
    is_verification: bool = False


@dataclass
class ExplanationTemplate:
    """Defines how a mathematical method should be taught step by step."""

    id: str
    method_id: str
    name_km: str
    name_en: str
    steps: list[ExplanationStepTemplate]
    verification_strategy: str = "expand_to_verify"  # "expand_to_verify", "substitute_root", "none"
    pedagogical_notes_km: str = ""
    pedagogical_notes_en: str = ""


@dataclass
class CurriculumExample:
    """Representative example problem for a method."""

    id: str
    problem_raw: str
    problem_latex: str
    solution_latex: str
    explanation_summary_km: str
    explanation_summary_en: str = ""
    method_id: str = ""


@dataclass
class Method:
    """A specific problem-solving method within a rule or concept."""

    id: str
    rule_id: str
    name_km: str
    name_en: str
    description_km: str
    description_en: str
    applicability: str  # Criteria when this method applies
    template: ExplanationTemplate | None = None
    examples: list[CurriculumExample] = field(default_factory=list)


@dataclass
class RuleFormula:
    """Mathematical rule, identity, or theorem."""

    id: str
    concept_id: str
    name_km: str
    name_en: str
    formula_latex: str  # e.g. "a^2 - b^2 = (a-b)(a+b)"
    condition_latex: str | None = None
    description_km: str = ""
    description_en: str = ""
    methods: list[Method] = field(default_factory=list)


@dataclass
class Concept:
    """Mathematical concept within a lesson."""

    id: str
    lesson_id: str
    order: int
    title_km: str
    title_en: str
    definition_km: str
    definition_en: str
    rules: list[RuleFormula] = field(default_factory=list)


@dataclass
class Lesson:
    """Curriculum lesson within a chapter."""

    id: str
    chapter_id: str
    order: int
    title_km: str
    title_en: str
    description_km: str
    description_en: str
    concepts: list[Concept] = field(default_factory=list)


@dataclass
class Chapter:
    """Curriculum chapter (aligned with MoEYS Grade 12 & Foundation curriculum)."""

    id: str
    domain: SubjectDomain
    order: int
    title_km: str
    title_en: str
    grade_level: int
    description_km: str
    description_en: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class LessonMetadata:
    """Lesson-awareness metadata attached to a solved problem."""

    chapter_id: str
    chapter_km: str
    chapter_en: str
    lesson_id: str
    lesson_km: str
    lesson_en: str
    concept_id: str
    concept_km: str
    concept_en: str
    method_id: str
    method_km: str
    method_en: str
    rule_name_km: str
    rule_name_en: str
    rule_formula: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapter_id": self.chapter_id,
            "chapter_km": self.chapter_km,
            "chapter_en": self.chapter_en,
            "lesson_id": self.lesson_id,
            "lesson_km": self.lesson_km,
            "lesson_en": self.lesson_en,
            "concept_id": self.concept_id,
            "concept_km": self.concept_km,
            "concept_en": self.concept_en,
            "method_id": self.method_id,
            "method_km": self.method_km,
            "method_en": self.method_en,
            "rule_name_km": self.rule_name_km,
            "rule_name_en": self.rule_name_en,
            "rule_formula": self.rule_formula,
        }
