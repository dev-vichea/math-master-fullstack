"""
Equations Lessons and Chapter (Linear and Quadratic Equations).
"""

from __future__ import annotations

from app.knowledge.methods.completing_square import method_completing_square
from app.knowledge.models import (
    Chapter,
    Concept,
    Lesson,
    RuleFormula,
    SubjectDomain,
)

rule_quadratic_formula = RuleFormula(
    id="rule_quadratic_formula",
    concept_id="concept_quadratic_equations",
    name_km="រូបមន្តឌីសគ្រីមីណង់ (ដីលតា)",
    name_en="Quadratic Formula via Discriminant Delta",
    formula_latex=r"\Delta = b^2 - 4ac, \quad x = \frac{-b \pm \sqrt{\Delta}}{2a}",
    description_km="រកឫសសមីការដឺក្រេទីពីរ ax² + bx + c = 0 តាមដីលតា។",
    description_en="Find roots of quadratic equation ax² + bx + c = 0 using discriminant.",
    methods=[method_completing_square],
)

concept_quadratic = Concept(
    id="concept_quadratic_equations",
    lesson_id="lesson_equations_quadratic",
    order=1,
    title_km="សមីការដឺក្រេទីពីរ (Quadratic Equations)",
    title_en="Quadratic Equations",
    definition_km="សមីការមានទម្រង់ ax² + bx + c = 0 ដែល a ≠ 0។",
    definition_en="Equations of form ax² + bx + c = 0 where a != 0.",
    rules=[rule_quadratic_formula],
)

lesson_equations = Lesson(
    id="lesson_equations_quadratic",
    chapter_id="chapter_equations",
    order=1,
    title_km="សមីការដឺក្រេទីពីរមានមួយអថេរ (Quadratic Equations)",
    title_en="Quadratic Equations with One Variable",
    description_km="វិធីដោះស្រាយសមីការដឺក្រេទីពីរតាមរូបមន្តដីលតា ឬការបំពេញជាការេពេញ។",
    description_en="Solving quadratic equations via discriminant formula or completing the square.",
    concepts=[concept_quadratic],
)

chapter_equations = Chapter(
    id="chapter_equations",
    domain=SubjectDomain.ALGEBRA,
    order=2,
    title_km="សមីការ និងប្រព័ន្ធសមីការ (Equations)",
    title_en="Equations and Systems",
    grade_level=10,
    description_km="ការដោះស្រាយសមីការលីនេអ៊ែរ និងសមីការដឺក្រេទីពីរ។",
    description_en="Solving linear and quadratic equations and equation systems.",
    lessons=[lesson_equations],
)
