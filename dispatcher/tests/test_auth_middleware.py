import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from shared.exceptions import UnauthorizedException, app_exception_handler, AppException

# Test için geçici bir FastAPI uygulaması kuruyoruz
app = FastAPI()
app.add_exception_handler(AppException, app_exception_handler)

async def mock_auth_dependency(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Eksik veya geçersiz token")
    
    token = auth_header.split(" ")[1]
    
    # Şimdilik basitçe token "valid_token" ise başarılı, değilse başarısız sayalım
    if token == "valid_token":
        return "testuser@example.com"
    else:
        raise UnauthorizedException("Geçersiz veya süresi dolmuş token")

# Korumalı (protected) bir test rotası
@app.get("/protected")
async def protected_route(user_email: str = Depends(mock_auth_dependency)):
    return {"message": "Giriş izni verildi", "user": user_email}

client = TestClient(app)

def test_protected_route_without_token():
    """Token olmadan yapılan istek 401 dönmeli."""
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"

def test_protected_route_with_invalid_token():
    """Geçersiz token ile yapılan istek 401 dönmeli."""
    response = client.get("/protected", headers={"Authorization": "Bearer fake_token"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"

def test_protected_route_with_valid_token():
    """Geçerli token ile yapılan istek başarılı olmalı ve kullanıcı bilgisini almalı."""
    response = client.get("/protected", headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    assert response.json()["user"] == "testuser@example.com"