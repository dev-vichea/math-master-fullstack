"""
Algebraic Expansion Methods Knowledge Base.
"""

from __future__ import annotations

from app.knowledge.explanation_templates.algebra import template_expansion_distributive
from app.knowledge.models import CurriculumExample, Method

# Method 1: Distributive Multiplication
method_distributive_multiplication = Method(
    id="method_distributive_multiplication",
    rule_id="rule_distributive_property",
    name_km="វិធីពន្លាតតាមលក្ខណៈបំបែកនៃផលគុណ",
    name_en="Distributive Property Expansion Method",
    description_km="គុណតួនីមួយៗនៃកត្តាទី១ ទៅលើគ្រប់តួនៃកត្តាទី២ រួចបង្រួមតួដូចគ្នា។",
    description_en="Multiply each term of the first factor by each term of the second factor, then collect like terms.",
    applicability="Expression is a product of two or more polynomials.",
    template=template_expansion_distributive,
    examples=[
        CurriculumExample(
            id="ex_exp_1",
            method_id="method_distributive_multiplication",
            problem_raw="(x + 1)(x - 2)",
            problem_latex=r"(x + 1)(x - 2)",
            solution_latex=r"x^2 - x - 2",
            explanation_summary_km="គុណពន្លាតបាន x² - 2x + x - 2 = x² - x - 2។",
        ),
    ],
)
