""" Request Logging Middleware Testleri"""
import pytest
from unittest.mock import MagicMock
from starlette.testclient import TestClient
from fastapi import FastAPI
from shared.middleware import LoggingMiddleware
@pytest.fixture
def mock_logger():
    return MagicMock()
@pytest.fixture
def app_with_middleware(mock_logger):
    """Middleware eklenmiş test oluşturur."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware, logger=mock_logger)
    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}
    return app
@pytest.fixture
def client(app_with_middleware):
    """ Test istemcisi """
    return TestClient(app_with_middleware)
def test_reponse_contains_x_time_header(client):
    """ Yanıtta X-Process-Time olmalı """
    reponse = client.get("/test")
    assert "X-Process-Time" in reponse.headers
def test_x_response_time_format_is_milliseconds(client):
    """X-Process-Time değeri 'ms' ile bitmeli."""
    response = client.get("/test")
    value = response.headers["X-Process-Time"]
    assert value.endswith("ms")
def test_middleware_does_not_block_response(client):
    """Middleware, normal yanıtı engellememeli."""
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}