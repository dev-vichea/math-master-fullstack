"""
Factorization Methods Knowledge Base.
"""

from __future__ import annotations

from app.knowledge.explanation_templates.algebra import (
    template_fact_common_factor,
    template_fact_diff_squares,
    template_fact_trinomial,
)
from app.knowledge.explanation_templates.calculus import template_limit_factor_cancel
from app.knowledge.models import CurriculumExample, Method

# Method 1: Common Factor Extraction
method_common_factor = Method(
    id="method_common_factor_extraction",
    rule_id="rule_common_factor",
    name_km="វិធីទាញកត្តារួម",
    name_en="Common Factor Extraction Method",
    description_km="អនុវត្តនៅពេលគ្រប់តួទាំងអស់ក្នុងកន្សោមមានកត្តាអថេរ ឬលេខរួមគ្នា។",
    description_en="Applies when all terms share a common numerical or variable factor.",
    applicability="All terms in the polynomial share a common divisor > 1 or common symbol.",
    template=template_fact_common_factor,
    examples=[
        CurriculumExample(
            id="ex_fact_1",
            method_id="method_common_factor_extraction",
            problem_raw="3x^2 + 6x",
            problem_latex=r"3x^2 + 6x",
            solution_latex=r"3x(x + 2)",
            explanation_summary_km="ទាញ 3x ជាកត្តារួមចេញក្រៅវង់ក្រចក។",
        ),
    ],
)

# Method 2: Difference of Two Squares
method_diff_squares = Method(
    id="method_diff_squares",
    rule_id="rule_diff_squares",
    name_km="វិធីផលសងការេ",
    name_en="Difference of Squares Method",
    description_km="ប្រើសម្រាប់ដាក់ជាផលគុណកត្តាកន្សោមរាង a² - b²។",
    description_en="Used for factoring expressions of the form a² - b².",
    applicability="Expression has two terms with opposite signs and both are perfect squares.",
    template=template_fact_diff_squares,
    examples=[
        CurriculumExample(
            id="ex_diff_sq_1",
            method_id="method_diff_squares",
            problem_raw="x^2 - 9",
            problem_latex=r"x^2 - 9",
            solution_latex=r"(x - 3)(x + 3)",
            explanation_summary_km="x² - 9 = x² - 3² = (x - 3)(x + 3)។",
        ),
    ],
)

# Method 3: Quadratic Trinomial Split
method_trinomial = Method(
    id="method_trinomial_split",
    rule_id="rule_trinomial_identity",
    name_km="វិធីបំបែកផលបូក-ផលគុណ",
    name_en="Sum-Product Factoring Method",
    description_km="ប្រើសម្រាប់ដាក់ជាផលគុណកត្តាត្រីធាដឺក្រេទីពីរ x² + bx + c។",
    description_en="Used for factoring quadratic trinomials of the form x² + bx + c.",
    applicability="Quadratic trinomial with leading coefficient 1.",
    template=template_fact_trinomial,
    examples=[
        CurriculumExample(
            id="ex_trinomial_1",
            method_id="method_trinomial_split",
            problem_raw="x^2 - 5x + 6",
            problem_latex=r"x^2 - 5x + 6",
            solution_latex=r"(x - 2)(x - 3)",
            explanation_summary_km="រកឃើញ -2 និង -3 (ផលបូក = -5, ផលគុណ = 6) នាំឱ្យបាន (x - 2)(x - 3)។",
        ),
    ],
)

# Method 4: Indeterminate Limit Factor Cancellation
method_limit_factor_cancel = Method(
    id="method_limit_factor_cancel",
    rule_id="rule_limit_factorization",
    name_km="វិធីដាក់ជាផលគុណកត្តាសម្រួលលីមីត",
    name_en="Indeterminate Limit Factorization & Cancellation Method",
    description_km="ដាក់ភាគយកនិងភាគបែងជាផលគុណកត្តា ដើម្បីសម្រួលកត្តាសូន្យ (x - c) នៃរាងមិនកំណត់ 0/0។",
    description_en="Factor numerator and denominator to cancel common zero factor (x - c) in 0/0 indeterminate form.",
    applicability="Indeterminate limit [0/0] involving polynomial quotient.",
    template=template_limit_factor_cancel,
    examples=[
        CurriculumExample(
            id="ex_limit_fact_1",
            method_id="method_limit_factor_cancel",
            problem_raw=r"\lim_{x \to 3} \frac{x^2 - 9}{x - 3}",
            problem_latex=r"\lim_{x \to 3} \frac{x^2 - 9}{x - 3}",
            solution_latex=r"6",
            explanation_summary_km="បំបែកភាគយក (x - 3)(x + 3) រួចសម្រួល (x - 3) ទទួលបាន lim_{x->3} (x + 3) = 6។",
        ),
    ],
)

