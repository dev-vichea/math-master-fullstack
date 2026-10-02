"""
Centralized structured logging configuration.

DEPRECATED: Import from app.core.logging instead.
This module is kept for backward compatibility only.
"""
from __future__ import annotations

from app.core.logging import (
    RequestIdFilter,
    get_logger,
    request_id_ctx,
    setup_logging,
)

__all__ = [
    "RequestIdFilter",
    "get_logger",
    "request_id_ctx",
    "setup_logging",
]
