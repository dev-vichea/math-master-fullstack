"""
Legacy alias for app.parser.exercise_parser.exercise_parser.
Deprecated: Use app.parser.exercise_parser instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "app.core.khmer.exercise_parser is deprecated. Use app.parser.exercise_parser instead.",
    DeprecationWarning,
    stacklevel=2,
)

from app.parser.exercise_parser.exercise_parser import (
    ParsedExercise,
    SubExercise,
    _extract_single_math_expression,
    _strip_non_math_words,
    parse_exercise,
)

__all__ = [
    "ParsedExercise",
    "SubExercise",
    "_extract_single_math_expression",
    "_strip_non_math_words",
    "parse_exercise",
]
