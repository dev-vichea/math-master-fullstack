"""
Curriculum Explanation Templates Package.
"""

from app.knowledge.explanation_templates.algebra import (
    template_expansion_distributive,
    template_fact_common_factor,
    template_fact_diff_squares,
    template_fact_trinomial,
)
from app.knowledge.explanation_templates.calculus import (
    template_derivative_step_by_step,
    template_limit_conjugate,
    template_limit_direct_substitution,
    template_limit_factor_cancel,
)
from app.knowledge.explanation_templates.complex_numbers import (
    template_complex_arithmetic,
)
from app.knowledge.explanation_templates.geometry import (
    template_vector_dot_product,
)

__all__ = [
    "template_expansion_distributive",
    "template_fact_common_factor",
    "template_fact_diff_squares",
    "template_fact_trinomial",
    "template_limit_direct_substitution",
    "template_limit_conjugate",
    "template_limit_factor_cancel",
    "template_derivative_step_by_step",
    "template_complex_arithmetic",
    "template_vector_dot_product",
]
