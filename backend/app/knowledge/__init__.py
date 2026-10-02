"""
Knowledge Base Module for Lesson-Aware Mathematics Instruction.
"""

from app.knowledge.bilingual_glossary import (
    ALL_MATH_TERMS,
    COMMAND_WORDS,
    EXAMPLE_USAGES,
    LOGICAL_CONNECTIVES,
    STRUCTURED_ENTRIES,
    GlossaryEntry,
    get_all_categories,
    lookup_english,
    lookup_khmer,
    search_glossary,
)
from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    ExplanationStepTemplate,
    ExplanationTemplate,
    Lesson,
    LessonMetadata,
    Method,
    RuleFormula,
    SubjectDomain,
)
from app.knowledge.registry import KnowledgeBaseRegistry, get_knowledge_registry

__all__ = [
    "ALL_MATH_TERMS",
    "COMMAND_WORDS",
    "Chapter",
    "Concept",
    "CurriculumExample",
    "EXAMPLE_USAGES",
    "ExplanationStepTemplate",
    "ExplanationTemplate",
    "GlossaryEntry",
    "KnowledgeBaseRegistry",
    "LOGICAL_CONNECTIVES",
    "Lesson",
    "LessonMetadata",
    "Method",
    "RuleFormula",
    "STRUCTURED_ENTRIES",
    "SubjectDomain",
    "get_all_categories",
    "get_knowledge_registry",
    "lookup_english",
    "lookup_khmer",
    "search_glossary",
]
