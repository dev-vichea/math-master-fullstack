"""
Curriculum Methods Package.
"""

from app.knowledge.methods.completing_square import method_completing_square
from app.knowledge.methods.conjugate import method_limit_conjugate
from app.knowledge.methods.expansion import method_distributive_multiplication
from app.knowledge.methods.factorization import (
    method_common_factor,
    method_diff_squares,
    method_limit_factor_cancel,
    method_trinomial,
)
from app.knowledge.methods.substitution import method_limit_direct_substitution

__all__ = [
    "method_common_factor",
    "method_diff_squares",
    "method_trinomial",
    "method_limit_factor_cancel",
    "method_distributive_multiplication",
    "method_limit_conjugate",
    "method_limit_direct_substitution",
    "method_completing_square",
]
