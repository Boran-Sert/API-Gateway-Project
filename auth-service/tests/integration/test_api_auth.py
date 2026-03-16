import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.api.router import get_auth_service
from app.services.auth_service import AuthService
from app.models.auth import UserCredential

# 1. SAHTE (MOCK) REPOSITORY
# product-service'de kullandığın yapıya benzer, tamamen hafızada çalışır.
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

# 2. MOCK DEPENDENCY INJECTION (Bağımlılık Ezme)
mock_repo = MockUserRepository()
mock_auth_service = AuthService(repository=mock_repo)

def override_get_auth_service():
    return mock_auth_service

# Gerçek servis yerine sahtesini bağla
app.dependency_overrides[get_auth_service] = override_get_auth_service

client = TestClient(app)

# 3. VERİTABANI SIFIRLAMA (Fixture)
@pytest.fixture(autouse=True)
def clear_mock_db():
    # Her test birbirinden bağımsız (izole) olması için listeyi temizler
    mock_repo.fake_db.clear()
    yield

# 4. TESTLER
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
    # Önce kullanıcıyı ekle
    client.post("/auth/register", json={"email": "test@example.com", "password": "test"}) 
    
    # İkinci defa aynı kayıt deneniyor
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "test"})
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error"]["detail"] == "Bu e-posta zaten kullanılıyor"

def test_api_login_success():
    """ Başarılı giriş işlemini test eder """
    client.post("/auth/register", json={"email": "login_test@example.com", "password": "test"})
    
    response = client.post("/auth/login", json={"email": "login_test@example.com", "password": "test"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Giriş başarılı"