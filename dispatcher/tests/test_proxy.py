""" Proxy Testleri """

from fastapi.testclient import TestClient
from dispatcher.app.main import app 
from unittest.mock import patch, AsyncMock
from httpx import Response, Request
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.fixture(autouse=True)
def disable_traffic_logging():
    with patch("dispatcher.app.main.log_traffic", new_callable=AsyncMock):
        yield

def test_dispatcher_health_returns_200():
    """ /health endpoint 200 döndürmeli sistem ayakta """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dispatcher"}

@patch("httpx.AsyncClient.request", new_callable=AsyncMock)
def test_dispatcher_routes_request_to_user_service(mock_request):
    """/api/users isteği user-service'e yönlendirilmeli."""
    
    # Hedef servisin döneceği sahte (mock)
    mock_request.return_value = Response(
        status_code=200, 
        json={"data": "mocked users"},
        request=Request("GET", "http://user-service:8002/users")
    )
    
    # Gateway'e istek 
    response = client.get("/api/users")
    
    # 1. Gateway 200 dönmeli
    assert response.status_code == 200
    # 2. Döndüğü veri bizim sahte veriyle aynı olmalı
    assert response.json() == {"data": "mocked users"}
    
    # 3. Gateway, hedef servise doğru URL ile istek atmış mı kontrol
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://user-service:8002/users"



@patch("httpx.AsyncClient.request", new_callable=AsyncMock)
def test_dispatcher_routes_request_to_product_service(mock_request):
    """/api/products isteği product-service'e yönlendirilmeli."""
    
    # 1. Hedef ürün servisinin döneceği sahte (mock) yanıtı hazırlıyoruz
    mock_request.return_value = Response(
        status_code=200, 
        json={"data": [{"id": "1", "name": "Test Ürünü", "price": 100}]},
        request=Request("GET", "http://product-service:8003/products")
    )
    
    # 2. Dışarıdaki bir kullanıcı gibi Gateway'e (Dispatcher) istek atıyoruz
    response = client.get("/api/products")
    
    # 3. Kontroller (Assertions)
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": "1", "name": "Test Ürünü", "price": 100}]}
    
    # 4. Gateway arka planda gerçekten product-service'in 8003 portuna gitmiş mi?
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["url"] == "http://product-service:8003/products"