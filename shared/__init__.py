"""shared/ — Tüm mikroservisler için ortak altyapı kütüphanesi"""

from shared.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ConflictException,
    ServiceUnavailableException,
    app_exception_handler,
)
from shared.hateoas import HateoasLink, HateoasBuilder
from shared.base_repository import AbstractRepository, MongoRepository
from shared.base_service import AbstractService
from shared.middleware import RequestLoggingMiddleware
from shared.metrics import REQUEST_COUNT, REQUEST_LATENCY, setup_metrics

__all__ = [
    # Hata Yönetimi
    "AppException",
    "NotFoundException",
    "UnauthorizedException",
    "ConflictException",
    "ServiceUnavailableException",
    "app_exception_handler",
    # HATEOAS
    "HateoasLink",
    "HateoasBuilder",
    # Repository Katmanı
    "AbstractRepository",
    "MongoRepository",
    # Service Katmanı
    "AbstractService",
    # Middleware
    "RequestLoggingMiddleware",
    # Metrics
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "setup_metrics",
]
