"""
Conjugate Methods Knowledge Base.
"""

from __future__ import annotations

from app.knowledge.explanation_templates.calculus import template_limit_conjugate
from app.knowledge.models import CurriculumExample, Method

# Method: Conjugate Rationalization for Limits
method_limit_conjugate = Method(
    id="method_limit_conjugate",
    rule_id="rule_conjugate_rationalization",
    name_km="វិធីគុណកន្សោមឆ្លាស់",
    name_en="Conjugate Rationalization Method",
    description_km="ប្រើសម្រាប់លីមីតរាងមិនកំណត់ [0/0] ដែលមានរ៉ាឌីកាល់ (ឫសការេ) ដើម្បីបំបាត់រ៉ាឌីកាល់ និងសម្រួលកត្តាសូន្យ។",
    description_en="Used for indeterminate limits [0/0] containing radicals to eliminate roots and cancel zero factors.",
    applicability="Limit approaches a finite point resulting in indeterminate form 0/0 involving radicals.",
    template=template_limit_conjugate,
    examples=[
        CurriculumExample(
            id="ex_limit_conj_1",
            method_id="method_limit_conjugate",
            problem_raw=r"\lim_{x \to 4} \frac{\sqrt{x} - 2}{x - 4}",
            problem_latex=r"\lim_{x \to 4} \frac{\sqrt{x} - 2}{x - 4}",
            solution_latex=r"\frac{1}{4}",
            explanation_summary_km="គុណកន្សោមឆ្លាស់ (√x + 2) លើភាគយកនិងភាគបែង រួចសម្រួល (x - 4) ទទួលបាន 1/(√4 + 2) = 1/4។",
        ),
    ],
)
