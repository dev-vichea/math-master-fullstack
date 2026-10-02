"""
Text normalization pipeline.

DEPRECATED: This module has been moved to app/parser/
Please update imports to use app.parser instead.
"""

import warnings

from app.parser.pipeline import NormalizationPipeline, NormalizationResult

warnings.warn(
    "app.core.normalization is deprecated. Please use app.parser instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["NormalizationPipeline", "NormalizationResult"]
