import httpx
from fastapi import Request
import re
from shared.exceptions import ServiceUnavailableException, UnauthorizedException
class Authenticator:
    """SRP uyumlu kimlik doğrulama sınıfı."""
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url.rstrip("/")
    async def extract_token(self, auth_header: str | None) -> str:
        """Header'dan Bearer formatını kontrol ederek token çıkarır (Bug #7)."""
        if not auth_header:
            raise UnauthorizedException("Authorization header missing")
        match = re.match(r"Bearer\s+(.+)", auth_header)
        if not match:
            raise UnauthorizedException("Authorization header must be Bearer token")
        return match.group(1)
    async def authenticate(self, request: Request) -> None:
        """Token'ı doğrular ve kullanıcı bilgilerini request state'e yazar."""
        auth_header = request.headers.get("Authorization")
        token = await self.extract_token(auth_header)
        client: httpx.AsyncClient = request.app.state.http_client
        validate_url = f"{self.auth_service_url}/auth/validate"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = await client.post(validate_url, headers=headers)
            resp.raise_for_status()
            user_data = resp.json()
            request.state.user_id = user_data.get("user_id")
            request.state.user_email = user_data.get("email")
            request.state.user_role = user_data.get("role")
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                raise UnauthorizedException(detail="Geçersiz token veya yetki")
            raise ServiceUnavailableException(f"Auth Service error: {e.response.status_code}")
        except httpx.RequestError:
            raise ServiceUnavailableException("Auth Service")