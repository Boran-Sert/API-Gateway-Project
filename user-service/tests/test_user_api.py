""" User Service API Testleri """

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app, get_user_service
from app.services.user_service import UserService

client = TestClient(app)


def _override_service(mock_service):
    """Gerçek servisi mock ile değiştirir."""
    app.dependency_overrides[get_user_service] = lambda: mock_service


def test_get_users_returns_hateoas_format():
    """/users endpoint'inin HATEOAS (_links) yapısında dönmesini test eder."""
    mock_service = AsyncMock(spec=UserService)
    mock_service.get_all.return_value = ([], 0)
    _override_service(mock_service)

    response = client.get("/users")

    assert response.status_code == 200

    json_data = response.json()
    assert "data" in json_data
    assert "_links" in json_data
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"].startswith("/users")


def test_get_empty_users_list():
    """Sistemde hiç kullanıcı yokken boş liste ve HATEOAS linkleri dönmelidir."""
    mock_service = AsyncMock(spec=UserService)
    mock_service.get_all.return_value = ([], 0)
    _override_service(mock_service)

    response = client.get("/users")

    assert response.status_code == 200

    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    assert "_links" in json_data
    assert "self" in json_data["_links"]

