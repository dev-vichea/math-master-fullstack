"""
Algebra Lessons and Chapter (Grade 9-12 Foundations).
"""

from __future__ import annotations

from app.knowledge.methods.expansion import method_distributive_multiplication
from app.knowledge.methods.factorization import (
    method_common_factor,
    method_diff_squares,
    method_trinomial,
)
from app.knowledge.models import (
    Chapter,
    Concept,
    Lesson,
    RuleFormula,
    SubjectDomain,
)

# --- Rules & Concepts for Expansion ---
rule_distributive = RuleFormula(
    id="rule_distributive_property",
    concept_id="concept_distributive_property",
    name_km="លក្ខណៈបំបែកនៃផលគុណចំពោះផលបូក",
    name_en="Distributive Property of Multiplication",
    formula_latex=r"(A + B)(C + D) = AC + AD + BC + BD",
    description_km="គុណគ្រប់តួនៃកត្តាទីមួយ ជាមួយគ្រប់តួនៃកត្តាទីពីរ។",
    description_en="Multiply each term in the first binomial by each term in the second binomial.",
    methods=[method_distributive_multiplication],
)

concept_distributive = Concept(
    id="concept_distributive_property",
    lesson_id="lesson_algebraic_expansion",
    order=1,
    title_km="លក្ខណៈបំបែកនៃផលគុណ (Distributive Property)",
    title_en="Distributive Property",
    definition_km="លក្ខណៈនៃប្រមាណវិធីគុណដែលចែកចាយទៅលើតួនីមួយៗនៃផលបូកឬផលដក។",
    definition_en="Property allowing multiplication to be distributed across terms of a sum or difference.",
    rules=[rule_distributive],
)

lesson_expansion = Lesson(
    id="lesson_algebraic_expansion",
    chapter_id="chapter_algebra_foundations",
    order=1,
    title_km="ការពន្លាតកន្សោមពិជគណិត (Algebraic Expansion)",
    title_en="Algebraic Expansion",
    description_km="ការពន្លាតផលគុណនៃពហុធា និងការប្រើប្រាស់រូបមន្តស្មើភាពសំខាន់ៗ។",
    description_en="Expanding polynomial products and applying algebraic identities.",
    concepts=[concept_distributive],
)

# --- Rules & Concepts for Factorization ---
rule_common_factor = RuleFormula(
    id="rule_common_factor",
    concept_id="concept_common_factor",
    name_km="រូបមន្តទាញកត្តារួម",
    name_en="Common Factor Identity",
    formula_latex=r"ka + kb = k(a + b)",
    description_km="កត្តារួម k អាចទាញចេញក្រៅផលបូកបាន។",
    description_en="A common factor k can be factored out of an algebraic sum.",
    methods=[method_common_factor],
)

concept_common_factor = Concept(
    id="concept_common_factor",
    lesson_id="lesson_factorization",
    order=1,
    title_km="កត្តារួម (Common Factor)",
    title_en="Common Factors",
    definition_km="កត្តាដែលចែកដាច់គ្រប់តួទាំងអស់ក្នុងកន្សោមពិជគណិត។",
    definition_en="A factor that divides every term in an algebraic expression.",
    rules=[rule_common_factor],
)

rule_diff_squares = RuleFormula(
    id="rule_diff_squares",
    concept_id="concept_special_identities",
    name_km="រូបមន្តផលសងការេ",
    name_en="Difference of Two Squares Identity",
    formula_latex=r"a^2 - b^2 = (a - b)(a + b)",
    description_km="ផលសងនៃការេពីរស្មើនឹងផលគុណនៃផលដកនិងផលបូករបស់វា។",
    description_en="The difference of two squares equals the product of their difference and sum.",
    methods=[method_diff_squares],
)

rule_trinomial = RuleFormula(
    id="rule_trinomial_identity",
    concept_id="concept_special_identities",
    name_km="រូបមន្តត្រីធាផលបូក-ផលគុណ",
    name_en="Quadratic Trinomial Identity",
    formula_latex=r"x^2 + (p + q)x + pq = (x + p)(x + q)",
    description_km="ត្រីធាអាចដាក់ជាផលគុណកត្តាតាមពីរចំនួនដែលបំពេញលក្ខខណ្ឌផលបូកនិងផលគុណ។",
    description_en="Trinomial factors into two binomials whose constants sum to b and multiply to c.",
    methods=[method_trinomial],
)

concept_special_identities = Concept(
    id="concept_special_identities",
    lesson_id="lesson_factorization",
    order=2,
    title_km="រូបមន្តស្មើភាពសំខាន់ៗ (Special Algebraic Identities)",
    title_en="Special Algebraic Identities",
    definition_km="រូបមន្តស្តង់ដារដែលអនុញ្ញាតឱ្យបំប្លែងផលបូក/ផលដកទៅជាផលគុណកត្តាដោយផ្ទាល់។",
    definition_en="Standard algebraic formulas allowing direct factorization of special binomials and polynomials.",
    rules=[rule_diff_squares, rule_trinomial],
)

lesson_factorization = Lesson(
    id="lesson_factorization",
    chapter_id="chapter_algebra_foundations",
    order=2,
    title_km="ការដាក់ជាផលគុណកត្តា (Factorization)",
    title_en="Polynomial Factorization",
    description_km="ការបំប្លែងពហុធាទៅជាផលគុណនៃកត្តាកម្រិតទាប តាមក្បួនគរុកោសល្យ។",
    description_en="Decomposing polynomials into products of simpler factors using pedagogical methods.",
    concepts=[concept_common_factor, concept_special_identities],
)

chapter_algebra = Chapter(
    id="chapter_algebra_foundations",
    domain=SubjectDomain.ALGEBRA,
    order=0,
    title_km="ពិជគណិតគ្រឹះ (Algebra Foundations)",
    title_en="Algebra Foundations",
    grade_level=10,
    description_km="ការពន្លាត ការដាក់ជាផលគុណកត្តា និងការគណនាកន្សោមពិជគណិត។",
    description_en="Polynomial expansion, factorization, and algebraic manipulations.",
    lessons=[lesson_expansion, lesson_factorization],
)
