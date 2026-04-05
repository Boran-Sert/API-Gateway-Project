import pytest
from fastapi import status
from fastapi.testclient import TestClient
from auth_app.main import app
from auth_app.api.router import get_auth_service
from auth_app.services.auth_service import AuthService
from auth_app.models.auth import UserCredential
class MockUserRepository:
    def __init__(self):
        self.fake_db = []
    async def find_by_email(self, email: str) -> UserCredential | None:
        for user in self.fake_db:
            if user.email == email:
                return user
        return None
    async def create(self, entity: UserCredential) -> UserCredential:
        self.fake_db.append(entity)
        return entity
mock_repo = MockUserRepository()
mock_auth_service = AuthService(repository=mock_repo)
def override_get_auth_service():
    return mock_auth_service
app.dependency_overrides[get_auth_service] = override_get_auth_service
client = TestClient(app)
@pytest.fixture(autouse=True)
def clear_mock_db():
    mock_repo.fake_db.clear()
    yield
def test_api_register_success():
    """ Başarılı bir kaydı test eder """
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "test"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "_id" in response.json()
    assert response.json()["email"] == "test@example.com"
def test_api_register_existing_email():
    """ Sistemde var olan email ile kayıt olma testi """
    client.post("/auth/register", json={"email": "test@example.com", "password": "test"}) 
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "test"})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error"]["detail"] == "Bu e-posta zaten kullanılıyor"
def test_api_login_success():
    """ Başarılı giriş işlemini test eder """
    client.post("/auth/register", json={"email": "login_test@example.com", "password": "test"})
    response = client.post("/auth/login", json={"email": "login_test@example.com", "password": "test"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "token" in response_data
def test_api_validate_success():
    """ Doğru bir token ile /validate işlemini test eder """
    client.post("/auth/register", json={"email": "validate_test@example.com", "password": "test"})
    res = client.post("/auth/login", json={"email": "validate_test@example.com", "password": "test"})
    token = res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    validate_res = client.post("/auth/validate", headers=headers)
    assert validate_res.status_code == status.HTTP_200_OK
    data = validate_res.json()
    assert data["email"] == "validate_test@example.com"
    assert "user_id" in data
    assert data["role"] == "user"
def test_api_validate_invalid_token():
    """ Geçersiz veya eksik token durumunda 401/403 dönmeli """
    headers = {"Authorization": "Bearer not.a.valid.token"}
    response = client.post("/auth/validate", headers=headers)
    assert response.status_code in [401, 403]