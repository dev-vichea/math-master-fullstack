"""
Completing the Square Methods Knowledge Base.
"""

from __future__ import annotations

from app.knowledge.models import CurriculumExample, Method

# Method: Completing the Square
method_completing_square = Method(
    id="method_completing_square",
    rule_id="rule_completing_square",
    name_km="វិធីបំពេញជាការេពេញ",
    name_en="Completing the Square Method",
    description_km="បំប្លែងកន្សោម x² + bx ទៅជាទម្រង់ការេពេញ (x + b/2)² - (b/2)²។",
    description_en="Rewrite x² + bx into perfect square form (x + b/2)² - (b/2)².",
    applicability="Quadratic expression or equation where completing the square is advantageous.",
    examples=[
        CurriculumExample(
            id="ex_comp_sq_1",
            method_id="method_completing_square",
            problem_raw="x^2 + 6x + 5",
            problem_latex=r"x^2 + 6x + 5",
            solution_latex=r"(x + 3)^2 - 4",
            explanation_summary_km="x² + 6x + 5 = (x + 3)² - 9 + 5 = (x + 3)² - 4។",
        ),
    ],
)
