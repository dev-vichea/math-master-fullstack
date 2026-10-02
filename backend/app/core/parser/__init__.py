"""
Mathematical expression parsing.

DEPRECATED: This module has been moved to app/parser/math_parser/
Please update imports to use app.parser instead.
"""

import warnings

from app.parser.math_parser.expression_parser import ParsedMath, parse_math_text

warnings.warn(
    "app.core.parser is deprecated. Please use app.parser.math_parser instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["parse_math_text", "ParsedMath"]
