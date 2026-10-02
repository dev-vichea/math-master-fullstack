"""
Custom application exception hierarchy.

All application-specific exceptions are defined here as the single canonical source.
"""

from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base class for application-specific exceptions."""

    def __init__(self, message: str, status_code: int = 400, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class MathProcessingError(AppException):
    """
    Raised for mathematical input parsing or solving issues
    (e.g., bad format, unrecognized intent, division by zero).
    """

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message=message, status_code=200, details=details)


class VisionProcessingError(AppException):
    """Raised for OCR or vision processing failures."""

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message=message, status_code=200, details=details)


class EntityNotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message=message, status_code=404, details=details)
