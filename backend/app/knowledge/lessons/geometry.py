"""
Geometry Lessons and Chapter (Spatial Analytic Geometry Grade 12).
"""

from __future__ import annotations

from app.knowledge.explanation_templates.geometry import template_vector_dot_product
from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    Lesson,
    Method,
    RuleFormula,
    SubjectDomain,
)

method_vector_dot = Method(
    id="method_vector_dot_product",
    rule_id="rule_vector_dot_product",
    name_km="វិធីគណនាផលគុណស្កាលែនៃពីរវ៉ិចទ័រ",
    name_en="Vector Dot Product Method",
    description_km="គណនាផលគុណស្កាលែតាមកូអរដោនេ u·v = x1*x2 + y1*y2 + z1*z2។",
    description_en="Compute dot product via coordinates: u·v = x1*x2 + y1*y2 + z1*z2.",
    applicability="Two 3D vectors with given numerical coordinates.",
    template=template_vector_dot_product,
    examples=[
        CurriculumExample(
            id="ex_geom_1",
            method_id="method_vector_dot_product",
            problem_raw=r"\vec{u}(1, 2, 3) \cdot \vec{v}(4, -1, 0)",
            problem_latex=r"\vec{u}(1, 2, 3) \cdot \vec{v}(4, -1, 0)",
            solution_latex=r"2",
            explanation_summary_km="1*4 + 2*(-1) + 3*0 = 4 - 2 + 0 = 2។",
        ),
    ],
)

rule_dot_product = RuleFormula(
    id="rule_vector_dot_product",
    concept_id="concept_spatial_vectors",
    name_km="រូបមន្តផលគុណស្កាលែតាមកូអរដោនេ",
    name_en="Vector Dot Product Coordinate Formula",
    formula_latex=r"\vec{u} \cdot \vec{v} = x_1 x_2 + y_1 y_2 + z_1 z_2",
    methods=[method_vector_dot],
)

concept_spatial_vectors = Concept(
    id="concept_spatial_vectors",
    lesson_id="lesson_spatial_vectors",
    order=1,
    title_km="វ៉ិចទ័រក្នុងលំហ (Vectors in Space)",
    title_en="Vectors in 3D Space",
    definition_km="ប្រមាណវិធីលើវ៉ិចទ័រក្នុងលំហ ផលគុណស្កាលែ និងផលគុណនៃពីរវ៉ិចទ័រ។",
    definition_en="Operations on spatial vectors, dot product, and cross product.",
    rules=[rule_dot_product],
)

lesson_spatial_geometry = Lesson(
    id="lesson_spatial_vectors",
    chapter_id="chapter_spatial_geometry",
    order=1,
    title_km="ធរណីមាត្រវិភាគក្នុងលំហ (Spatial Analytic Geometry)",
    title_en="Spatial Analytic Geometry",
    description_km="កូអរដោនេក្នុងលំហ វ៉ិចទ័រ ប្លង់ និងបន្ទាត់ក្នុងលំហ។",
    description_en="Spatial coordinates, vectors, planes, and lines in 3D space.",
    concepts=[concept_spatial_vectors],
)

chapter_geometry = Chapter(
    id="chapter_spatial_geometry",
    domain=SubjectDomain.GEOMETRY,
    order=6,
    title_km="ជំពូកទី៥ : ធរណីមាត្រក្នុងលំហ (Spatial Geometry)",
    title_en="Chapter 5: Spatial Geometry",
    grade_level=12,
    description_km="ធរណីមាត្រវិភាគក្នុងលំហ និងប្រព័ន្ធកូអរដោនេ។",
    description_en="Spatial analytic geometry and 3D coordinate systems.",
    lessons=[lesson_spatial_geometry],
)
