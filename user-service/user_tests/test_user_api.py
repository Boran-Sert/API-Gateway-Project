""" User Service API Testleri """
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from user_service_app.main import app, get_user_service
from user_service_app.services.user_service import UserService
from user_service_app.models.user import User
client = TestClient(app)
def _override_service(mock_service):
    """Gerçek servisi mock ile değiştirir."""
    app.dependency_overrides[get_user_service] = lambda: mock_service
def test_get_my_profile():
    """/users/me endpoint test."""
    mock_service = AsyncMock(spec=UserService)
    mock_user = User(username="test_user", email="test@example.com")
    mock_service.get_my_profile.return_value = mock_user
    _override_service(mock_service)
    response = client.get(
        "/users/me",
        headers={"X-User-ID": mock_user.id, "X-User-Email": "test@example.com"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["email"] == "test@example.com"
    assert json_data["username"] == "test_user"
def test_update_my_profile():
    """/users/me PUT endpoint test."""
    mock_service = AsyncMock(spec=UserService)
    mock_user = User(username="updated_user", email="test@example.com", bio="New bio")
    mock_service.update_my_profile.return_value = mock_user
    _override_service(mock_service)
    response = client.put(
        "/users/me",
        json={"username": "updated_user", "bio": "New bio"},
        headers={"X-User-ID": mock_user.id, "X-User-Email": "test@example.com"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["username"] == "updated_user"
    assert json_data["bio"] == "New bio"