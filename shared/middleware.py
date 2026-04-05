"""Ortak middleware — İstek loglama ve süre ölçümü"""
import time
from logging import LoggerAdapter
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Gelen her HTTP isteğini yapılandırılmış bir logger kullanarak loglar.
    İstek başlangıcını, bitişini ve olası hataları kaydeder.
    """
    def __init__(self, app: ASGIApp, logger: LoggerAdapter):
        super().__init__(app)
        self.logger = logger
    async def dispatch(self, request: Request, call_next):
        """İsteği yakalar, süreyi ölçer, loglar ve yanıtı döner."""
        start_time = time.perf_counter()
        self.logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "request_id": request.headers.get("X-Request-ID"),              
                "user_id": request.headers.get("X-User-ID"),                               
            }
        )
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time_ms = (time.perf_counter() - start_time) * 1000
            status_code = 500                                                  
            self.logger.exception(                                                        
                "Request failed with unhandled exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "process_time_ms": f"{process_time_ms:.2f}",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "request_id": request.headers.get("X-Request-ID"),
                    "user_id": request.headers.get("X-User-ID"),
                }
            )
            raise exc                           
        process_time_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code
        log_level_func = self.logger.info
        if 400 <= status_code < 500:
            log_level_func = self.logger.warning
        elif status_code >= 500:
            log_level_func = self.logger.error
        log_level_func(
            "Request finished",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "process_time_ms": f"{process_time_ms:.2f}",
                "request_id": request.headers.get("X-Request-ID"),
                "user_id": request.headers.get("X-User-ID"),
            }
        )
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        return response