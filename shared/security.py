"""Yetkilendirme ve rol kontrolü için yardımcı fonksiyonlar."""
from fastapi import Header, Depends
from typing import List
from shared.exceptions import ForbiddenException
async def get_user_role(x_user_role: str = Header(..., alias="X-User-Role")) -> str:
    """
    Gelen isteğin başlıklarından (X-User-Role) kullanıcının rolünü çeker.
    Dispatcher'ın token'ı doğrulayıp bu başlığı eklediği varsayılır.
    """
    return x_user_role
class RoleChecker:
    """FastAPI bağımlılığı olarak kullanılacak rol kontrol sınıfı."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    async def __call__(self, user_role: str = Depends(get_user_role)):
        if user_role not in self.allowed_roles:
            raise ForbiddenException(f"Bu işlem için yetkiniz yok. Gerekli roller: {', '.join(self.allowed_roles)}")