"""
Central Knowledge Base Registry for Lesson-Aware Mathematics Instruction.
"""

from __future__ import annotations

from typing import Any

from app.knowledge.curriculum_data import build_curriculum_knowledge
from app.knowledge.models import Chapter, Lesson, LessonMetadata, Method


class KnowledgeBaseRegistry:
    """Singleton registry indexing all chapters, lessons, concepts, rules, and methods."""

    def __init__(self) -> None:
        self.chapters: list[Chapter] = build_curriculum_knowledge()
        self._chapters_by_id: dict[str, Chapter] = {}
        self._lessons_by_id: dict[str, Lesson] = {}
        self._methods_by_id: dict[str, Method] = {}
        self._metadata_by_method_id: dict[str, LessonMetadata] = {}

        self._build_indices()

    def _build_indices(self) -> None:
        """Indexes curriculum tree for constant-time lookup."""
        for chapter in self.chapters:
            self._chapters_by_id[chapter.id] = chapter
            for lesson in chapter.lessons:
                self._lessons_by_id[lesson.id] = lesson
                for concept in lesson.concepts:
                    for rule in concept.rules:
                        for method in rule.methods:
                            self._methods_by_id[method.id] = method
                            self._metadata_by_method_id[method.id] = LessonMetadata(
                                chapter_id=chapter.id,
                                chapter_km=chapter.title_km,
                                chapter_en=chapter.title_en,
                                lesson_id=lesson.id,
                                lesson_km=lesson.title_km,
                                lesson_en=lesson.title_en,
                                concept_id=concept.id,
                                concept_km=concept.title_km,
                                concept_en=concept.title_en,
                                method_id=method.id,
                                method_km=method.name_km,
                                method_en=method.name_en,
                                rule_name_km=rule.name_km,
                                rule_name_en=rule.name_en,
                                rule_formula=rule.formula_latex,
                            )

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        return self._chapters_by_id.get(chapter_id)

    def get_lesson(self, lesson_id: str) -> Lesson | None:
        return self._lessons_by_id.get(lesson_id)

    def get_method(self, method_id: str) -> Method | None:
        return self._methods_by_id.get(method_id)

    def get_metadata(self, method_id: str) -> LessonMetadata | None:
        return self._metadata_by_method_id.get(method_id)

    def get_all_chapters(self) -> list[Chapter]:
        return self.chapters


_global_registry: KnowledgeBaseRegistry | None = None


def get_knowledge_registry() -> KnowledgeBaseRegistry:
    """Returns the singleton KnowledgeBaseRegistry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = KnowledgeBaseRegistry()
    return _global_registry
