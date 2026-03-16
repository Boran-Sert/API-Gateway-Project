""" Unit testleri için AuthService test dosyası """

import pytest
from unittest.mock import AsyncMock, patch
from app.services.auth_service import AuthService
from app.models.auth import RegisterRequest


@pytest.mark.asyncio
@patch("app.services.auth_service.hash_password", return_value="fake_hashed_pw")
async def test_register_user_success(mock_hash):
    mock_repo = AsyncMock()
    mock_repo.find_by_email.return_value = None
    
    service = AuthService(repository=mock_repo)
    request = RegisterRequest(email="test@example.com", password="password123")
    
    user = await service.register(request)
    
    assert user.email == "test@example.com"
    mock_repo.create.assert_called_once()
    mock_hash.assert_called_once_with("password123")
