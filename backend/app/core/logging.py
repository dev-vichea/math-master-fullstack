"""
Centralized structured logging configuration.

Supports correlation ID tracking (X-Request-ID) across request lifecycles.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

# Context variable holding the correlation ID for the current request
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Injects the current request correlation ID into the log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "-"
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configures the root and application loggers with formatted output."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(name)s]: %(message)s"
    formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence overly verbose external libraries if desired
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.access").addFilter(RequestIdFilter())


def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance with request ID filter applied."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())
    return logger
