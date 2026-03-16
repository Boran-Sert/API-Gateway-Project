import pytest
from unittest.mock import AsyncMock
from app.services.auth_service import AuthService
from app.models.auth import RegisterRequest
""" Unit testleri için AuthService test dosyası """

@pytest.mark.asyncio
async def test_register_user_success():
    mock_repo = AsyncMock()
    mock_repo.find_by_email.return_value = None
    
    service = AuthService(repository=mock_repo)
    request = RegisterRequest(email="test@example.com", password="password123")
    
    user = await service.register(request)
    
    assert user.email == "test@example.com"
    mock_repo.create.assert_called_once()
