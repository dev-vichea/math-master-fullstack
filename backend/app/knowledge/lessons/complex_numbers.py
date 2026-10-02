"""
Complex Numbers Lessons and Chapter (Grade 12 BacII Focus).
"""

from __future__ import annotations

from app.knowledge.explanation_templates.complex_numbers import template_complex_arithmetic
from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    Lesson,
    Method,
    RuleFormula,
    SubjectDomain,
)

method_complex_algebraic = Method(
    id="method_complex_arithmetic",
    rule_id="rule_complex_arithmetic",
    name_km="ប្រមាណវិធីលើទម្រង់ពីជគណិតនៃចំនួនកុំផ្លិច",
    name_en="Arithmetic Operations on Algebraic Form",
    description_km="បូក ដក គុណ ចំនួនកុំផ្លិចដោយចាត់ទុក i² = -1។",
    description_en="Perform addition, subtraction, and multiplication of complex numbers with i² = -1.",
    applicability="Expressions involving complex numbers in algebraic form a + bi.",
    template=template_complex_arithmetic,
    examples=[
        CurriculumExample(
            id="ex_cplx_1",
            method_id="method_complex_arithmetic",
            problem_raw="(2 + 3i) + (4 - 5i)",
            problem_latex=r"(2 + 3i) + (4 - 5i)",
            solution_latex=r"6 - 2i",
            explanation_summary_km="បូកផ្នែកពិត (2+4) និងផ្នែកនិម្មិត (3-5)i ទទួលបាន 6 - 2i។",
        ),
    ],
)

rule_complex_arithmetic = RuleFormula(
    id="rule_complex_arithmetic",
    concept_id="concept_complex_algebraic_form",
    name_km="ប្រមាណវិធីលើចំនួនកុំផ្លិច",
    name_en="Complex Number Arithmetic Identity",
    formula_latex=r"(a + bi) \pm (c + di) = (a \pm c) + (b \pm d)i",
    methods=[method_complex_algebraic],
)

concept_complex_algebraic = Concept(
    id="concept_complex_algebraic_form",
    lesson_id="lesson_complex_numbers_intro",
    order=1,
    title_km="ទម្រង់ពីជគណិតនៃចំនួនកុំផ្លិច (Algebraic Form)",
    title_en="Algebraic Form of Complex Numbers",
    definition_km="ចំនួនកុំផ្លិច z = a + bi ដែល a ជាផ្នែកពិត និង b ជាផ្នែកនិម្មិត (i² = -1)។",
    definition_en="A complex number z = a + bi with real part a and imaginary part b where i² = -1.",
    rules=[rule_complex_arithmetic],
)

lesson_complex_numbers = Lesson(
    id="lesson_complex_numbers_intro",
    chapter_id="chapter_complex_numbers",
    order=1,
    title_km="ចំនួនកុំផ្លិច (Complex Numbers)",
    title_en="Complex Numbers",
    description_km="ទម្រង់ពីជគណិត ទម្រង់ត្រីកោណមាត្រ និងប្រមាណវិធីលើចំនួនកុំផ្លិច។",
    description_en="Algebraic and trigonometric forms of complex numbers and operations.",
    concepts=[concept_complex_algebraic],
)

chapter_complex_numbers = Chapter(
    id="chapter_complex_numbers",
    domain=SubjectDomain.ALGEBRA,
    order=3,
    title_km="ជំពូកទី២ : ចំនួនកុំផ្លិច (Complex Numbers)",
    title_en="Chapter 2: Complex Numbers",
    grade_level=12,
    description_km="ចំនួនកុំផ្លិច និងអនុវត្តន៍ក្នុងធរណីមាត្រ។",
    description_en="Complex numbers and geometric applications.",
    lessons=[lesson_complex_numbers],
)
