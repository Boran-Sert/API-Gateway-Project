"""Ortak middleware — İstek loglama ve süre ölçümü"""

import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Gelen her HTTP isteğini loglar ve yanıta süre bilgisi ekler."""

    async def dispatch(self, request: Request, call_next):
        """İsteği yakalar, süreyi ölçer, loglar ve yanıtı döner."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response
