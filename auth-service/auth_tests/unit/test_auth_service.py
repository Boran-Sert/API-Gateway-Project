""" Unit testleri için AuthService test dosyası """

import pytest
from unittest.mock import AsyncMock, patch
from auth_app.services.auth_service import AuthService
from auth_app.models.auth import RegisterRequest, LoginRequest
import jwt


@pytest.mark.asyncio
@patch("auth_app.services.auth_service.hash_password", return_value="fake_hashed_pw")
async def test_register_user_success(mock_hash):
    mock_repo = AsyncMock()
    mock_repo.find_by_email.return_value = None
    
    service = AuthService(repository=mock_repo)
    request = RegisterRequest(email="test@example.com", password="password123")
    
    user = await service.register(request)
    
    assert user.email == "test@example.com"
    mock_repo.create.assert_called_once()
    mock_hash.assert_called_once_with("password123")

@pytest.mark.asyncio
@patch("auth_app.services.auth_service.hash_password", return_value="fake_hashed_pw")
@patch("auth_app.services.auth_service.verify_password", return_value=True)
async def test_login_returns_jwt_token(mock_verify, mock_hash):
    """ Login başarlı olduğunda token dönmeli """
    mock_repo = AsyncMock()

    mock_repo.find_by_email.return_value = AsyncMock(
        email = "test@example.com",
        hashed_password = "fake_pw"
    )

    service = AuthService(repository =mock_repo)
    request = LoginRequest(email= "test@example.com", password = "password123")
    result = await service.login(request)

    # 1 sonuç bir token içermeli
    assert "token" in result

    # 2 token decode edilmeli ve içinde doğru email olmalı
    decoded = jwt.decode(result["token"], options = {"verify_signature": False})
    assert decoded["sub"] == "test@example.com"


@pytest.mark.asyncio
@patch("auth_app.services.auth_service.hash_password", return_value="fake_hashed_pw")
@patch("auth_app.services.auth_service.verify_password", return_value=True)
async def test_login_saves_token_to_redis(mock_verify, mock_hash):
    """ Token başarlı olduğunda REDİS'e kaydetmeli """
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()

    # Kullanıcı veritabanında varmış gibi davran
    mock_repo.find_by_email.return_value = AsyncMock(
        email = "test@example.com",
        hashed_password = "fakepsw"
    )

    service = AuthService(repository = mock_repo, redis_client = mock_redis)
    request = LoginRequest(email = "test@example.com", password = "pas123")
    result = await service.login(request)

    #1. Redis set
    mock_redis.set.assert_called_once()

    #2. Argüman kontrol
    args, kwargs = mock_redis.set.call_args
    assert args[0] == f"token:{result['token']}"
    assert args[1] == "test@example.com"
    assert kwargs["ex"] == 3600 