from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator
SERVICE_INFO = Info("service_info", "Servis bilgisi")
def setup_metrics(app, service_name: str):
    """FastAPI uygulamasına /metrics endpoint'ini ekler."""
    SERVICE_INFO.info({"name": service_name, "version": "1.0.0"})
    Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics")