from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_register_success():
    """ Başarılı bir kayıtı test eder """
    response = client.post(
        "/auth/register",
        json = {"email": "test@example.com", "password": "test"}
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == "test@example.com"


def test_api_register_existing_email():
    """ Sistemde var olan email ile kayıt olma testi """
    client.post("/auth/register",
    json ={"email": "test@example.com", "password": "test"}) 
    

    response = client.post("/auth/register",
    json = {"email": "test@example.com", "password": "test"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Bu e-posta adresi zaten kullanımda."

def test_api_login_success():
    # Pre-register for login test
    client.post("/auth/register",
        json={"email": "login_test@example.com", "password": "test"}
    )
    
    response = client.post("/auth/login",
    json = {"email": "login_test@example.com", "password": "test"}
    )
    assert response.status_code == 200
    assert "token" in response.json()