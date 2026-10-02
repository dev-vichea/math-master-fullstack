"""
Bilingual explanation generation.

DEPRECATED: This module has been moved to app/explanation/templates/
Please update imports to use app.explanation instead.
"""

import warnings

from app.explanation.templates.templates import ExplanationGenerator, get_explanation_generator

warnings.warn(
    "app.core.localization is deprecated. Please use app.explanation instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ExplanationGenerator", "get_explanation_generator"]
