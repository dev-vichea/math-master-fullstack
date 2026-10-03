"""
Curriculum Knowledge Base for Cambodian High School Mathematics (MoEYS Grade 12 & Foundation).

Organized as:
Chapter → Lesson → Concept → Rule/Formula → Method → Explanation Template → Examples

Modularized across:
- app.knowledge.lessons.*
- app.knowledge.methods.*
- app.knowledge.explanation_templates.*
"""

from __future__ import annotations

from app.knowledge.lessons import (
    chapter_algebra,
    chapter_complex_numbers,
    chapter_derivatives,
    chapter_differential_equations,
    chapter_equations,
    chapter_geometry,
    chapter_integrals,
    chapter_limits,
    chapter_logarithms,
    chapter_sequences,
)
from app.knowledge.models import Chapter


def build_curriculum_knowledge() -> list[Chapter]:
    """Builds and returns the full structured curriculum knowledge base."""
    return [
        chapter_algebra,
        chapter_limits,
        chapter_equations,
        chapter_complex_numbers,
        chapter_derivatives,
        chapter_logarithms,
        chapter_integrals,
        chapter_differential_equations,
        chapter_sequences,
        chapter_geometry,
    ]

