""" Request Logging Middleware Testleri"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from starlette.testclient import TestClient
from fastapi import FastAPI
from shared.middleware import RequestLoggingMiddleware

@pytest.fixture
def app_with_middleware():
    """Middleware eklenmiş test oluşturur."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}
    return app

@pytest.fixture
def client(app_with_middleware):
    """ Test istemcisi """
    return TestClient(app_with_middleware)

    def test_reponse_contains_x_time_header(client):
        """ Yanıtta X- response - time olmalı """
        reponse = client.get("/test")
        assert "X-Response-Time" in reponse.headers

def test_x_response_time_format_is_milliseconds(client):
    """X-Response-Time değeri 'ms' ile bitmeli."""
    response = client.get("/test")
    value = response.headers["X-Response-Time"]
    assert value.endswith("ms")

def test_middleware_does_not_block_response(client):
    """Middleware, normal yanıtı engellememeli."""
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    