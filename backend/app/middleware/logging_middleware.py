"""
Request/response logging middleware with context propagation.

Logs all API requests with timing, payload metadata, and response status.
Adds request_id to all log messages for correlation.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import get_logger

logger = get_logger("app.middleware.request_logging")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging.
    
    Features:
    - Request ID generation and propagation
    - Request timing
    - Payload size tracking
    - Response status logging
    - Error tracking
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request start
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )
        
        # Track payload size for file uploads
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size_bytes = int(content_length)
                size_mb = size_bytes / 1024 / 1024
                logger.debug(
                    f"Request payload: {size_mb:.2f} MB",
                    extra={"request_id": request_id, "size_bytes": size_bytes}
                )
                
                # Record metric
                try:
                    from app.monitoring import record_image_size
                    if "image" in path or "vision" in path or "ocr" in path:
                        record_image_size(size_bytes)
                except ImportError:
                    pass
                    
            except ValueError:
                pass
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": f"{duration_ms:.2f}",
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {exc}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": f"{duration_ms:.2f}",
                    "error": str(exc),
                },
                exc_info=True
            )
            raise


class StructuredLoggingContext:
    """
    Context manager for structured logging with additional fields.
    
    Usage:
        with StructuredLoggingContext(request_id=req_id, user_id=user):
            logger.info("Processing request")
            # All logs will include request_id and user_id
    """
    
    def __init__(self, **context):
        """Initialize with context fields."""
        self.context = context
        self._original_factory = None
    
    def __enter__(self):
        """Add context to logging."""
        # Store original log record factory
        import logging
        self._original_factory = logging.getLogRecordFactory()
        
        # Create new factory that adds context
        def record_factory(*args, **kwargs):
            record = self._original_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original factory."""
        import logging
        if self._original_factory:
            logging.setLogRecordFactory(self._original_factory)


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        Request ID or 'unknown' if not set
    """
    return getattr(request.state, 'request_id', 'unknown')
