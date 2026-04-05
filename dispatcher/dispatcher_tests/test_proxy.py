""" Proxy Testleri """
from fastapi.testclient import TestClient
from dispatcher_app.main import app 
from unittest.mock import patch, AsyncMock
from httpx import Response, Request
import pytest
client = TestClient(app)
def test_dispatcher_health_returns_200():
    """ /health endpoint 200 döndürmeli sistem ayakta """
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dispatcher"}
@patch("dispatcher_app.main.authenticator.authenticate", new_callable=AsyncMock)
@patch("httpx.AsyncClient.request", new_callable=AsyncMock)
def test_dispatcher_routes_request_to_user_service(mock_request, mock_auth):
    """/api/users isteği user-service'e yönlendirilmeli (auth mocklanarak)."""
    mock_auth.return_value = None
    mock_request.return_value = Response(
        status_code=200, 
        json={"data": "mocked users"},
        request=Request("GET", "http://user-service:8002/")                              
    )
    with TestClient(app) as client:
        response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == {"data": "mocked users"}
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://user-service:8002/"
@patch("dispatcher_app.main.authenticator.authenticate", new_callable=AsyncMock)
@patch("httpx.AsyncClient.request", new_callable=AsyncMock)
def test_dispatcher_routes_request_to_product_service(mock_request, mock_auth):
    """/api/products isteği product-service'e yönlendirilmeli."""
    mock_auth.return_value = None
    mock_request.return_value = Response(
        status_code=200, 
        json={"data": [{"id": "1", "name": "Test Ürünü", "price": 100}]},
        request=Request("GET", "http://product-service:8003/")
    )
    with TestClient(app) as client:
        response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "1", "name": "Test Ürünü", "price": 100}]}
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://product-service:8003/"