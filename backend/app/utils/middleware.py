"""
Application middleware for request correlation, latency tracking, and access logging.

DEPRECATED: Import from app.core.middleware instead.
This module is kept for backward compatibility only.
"""
from __future__ import annotations

from app.core.middleware import RequestCorrelationMiddleware

__all__ = ["RequestCorrelationMiddleware"]
