"""
Custom application exception hierarchy.

DEPRECATED: Import from app.core.exceptions instead.
This module is kept for backward compatibility only.
"""
from __future__ import annotations

from app.core.exceptions import (
    AppException,
    EntityNotFoundError,
    MathProcessingError,
    VisionProcessingError,
)

__all__ = [
    "AppException",
    "EntityNotFoundError",
    "MathProcessingError",
    "VisionProcessingError",
]
