""" User Service API Testleri """

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app, get_user_service
from app.services.user_service import UserService

client = TestClient(app)

def test_get_users_returns_hateoas_format():
    """/users endpoint'inin HATEOAS (_links) yapısında dönmesini test eder."""
    
    # 1. Mock UserService oluştur
    mock_service = AsyncMock(spec=UserService)
    mock_service.get_all.return_value = ([], 0)  # Boş liste ve 0 toplam döner
    
    # 2. Dependency Injection'ı ez (Gerçek veritabanına bağlanmasını engelle)
    app.dependency_overrides[get_user_service] = lambda: mock_service

    response = client.get("/users")

    # HTTP 200 dönmeli
    assert response.status_code == 200

    # Cevabın içinde HATEOAS için _links olmlaı ve asıl veri data içinde olmalı
    json_data = response.json()
    assert "data" in json_data
    assert "_links" in json_data

    # kendi kendine self linkine sahip olmalı
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"].startswith("/users")