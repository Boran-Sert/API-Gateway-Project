"""Prometheus metrikleri — Tüm servisler için ortak izleme altyapısı"""

from prometheus_client import Counter, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Toplam HTTP istek sayısı",
    ["method", "endpoint", "status_code", "service"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP istek süresi (saniye)",
    ["method", "endpoint", "service"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

SERVICE_INFO = Info("service_info", "Servis bilgisi")


def setup_metrics(app, service_name: str):
    """FastAPI uygulamasına /metrics endpoint'ini ve Prometheus izlemesini ekler."""
    SERVICE_INFO.info({"name": service_name, "version": "1.0.0"})
    Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics")
