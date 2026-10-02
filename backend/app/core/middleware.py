"""
Application middleware for request correlation, latency tracking, and access logging.
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("app.middleware")


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Extracts or generates a unique correlation ID (X-Request-ID).
    2. Attaches the correlation ID to the logging ContextVar.
    3. Measures request execution duration.
    4. Logs request/response details.
    5. Returns the X-Request-ID header in the response.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(req_id)

        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(f"Started {request.method} {request.url.path} from {client_host}")

        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            response.headers["X-Request-ID"] = req_id
            response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"

            logger.info(
                f"Finished {request.method} {request.url.path} - "
                f"Status: {response.status_code} in {elapsed_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"Failed {request.method} {request.url.path} after {elapsed_ms:.2f}ms: {exc}",
                exc_info=True,
            )
            raise
        finally:
            request_id_ctx.reset(token)
