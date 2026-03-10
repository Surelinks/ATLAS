"""
Atlas AI - Request Middleware
==============================
Provides request logging, timing, and request-ID injection for all
incoming HTTP requests.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

import time
import uuid
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    - Assigns every request a unique ``X-Request-ID`` header.
    - Logs method, path, status code, and elapsed time for each request.
    - Propagates the request ID back to the client in the response headers.

    Usage::

        app.add_middleware(RequestLoggingMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Store request ID so downstream handlers can reference it
        request.state.request_id = request_id

        try:
            response: Response = await call_next(request)
        except Exception as exc:  # pragma: no cover
            logger.exception(
                "Unhandled exception | request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            raise exc

        elapsed_ms = (time.perf_counter() - start_time) * 1_000

        logger.info(
            "request_id=%s method=%s path=%s status=%s duration=%.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
        return response
