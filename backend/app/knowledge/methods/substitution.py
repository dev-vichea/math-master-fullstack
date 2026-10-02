"""
Substitution Methods Knowledge Base.
"""

from __future__ import annotations

from app.knowledge.explanation_templates.calculus import template_limit_direct_substitution
from app.knowledge.models import CurriculumExample, Method

# Method 1: Direct Substitution for Limits (Continuous Functions)
method_limit_direct_substitution = Method(
    id="method_limit_direct_substitution",
    rule_id="rule_limit_direct_substitution",
    name_km="វិធីជំនួសតម្លៃផ្ទាល់សម្រាប់អនុគមន៍ជាប់",
    name_en="Direct Substitution Method for Continuous Functions",
    description_km="គណនាតម្លៃលីមីតដោយជំនួស x = c ផ្ទាល់ចូលក្នុងអនុគមន៍ f(x) ប្រសិនបើ f កំណត់ និងជាប់ត្រង់ c។",
    description_en="Evaluate limit by directly substituting x = c into f(x) when f is continuous and defined at c.",
    applicability="Limit as x approaches a finite real number c where f(c) is well-defined and continuous.",
    template=template_limit_direct_substitution,
    examples=[
        CurriculumExample(
            id="ex_limit_subst_1",
            method_id="method_limit_direct_substitution",
            problem_raw=r"\lim_{x \to 2} \sqrt{x}",
            problem_latex=r"\lim_{x \to 2} \sqrt{x}",
            solution_latex=r"\sqrt{2}",
            explanation_summary_km="ដោយសារអនុគមន៍ f(x) = √x ជាប់ត្រង់ x = 2 នោះ lim_{x->2} √x = √2។",
        ),
    ],
)
