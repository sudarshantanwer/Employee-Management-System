"""Request logging middleware using Loguru."""

import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, duration, and user."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "unknown")
        user_id = getattr(request.state, "user_id", "anonymous")

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        user_id = getattr(request.state, "user_id", user_id)

        logger = get_request_logger(request_id, user_id)
        logger.info(
            "method={} path={} status_code={} duration_ms={:.2f}",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
