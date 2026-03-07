from shared.base_service import AbstractService
from shared.base_repository import AbstractRepository
from app.models.user import User

class UserService(AbstractService[User]):
    """
    Kullanıcılarla ilgili iş kurallarının (business logic) çalıştığı servis sınıfı.
    Repository'yi dışarıdan (Dependency Injection ile) alır.
    """
    def __init__(self, repository: AbstractRepository[User]):
        super().__init__(repository)
        
    async def get_all(self, page: int = 1, per_page: int = 10) -> tuple[list[User], int]:
        """Tüm kullanıcıları sayfalı olarak getirir."""
        skip = (page - 1) * per_page
        items = await self._repository.find_all(skip=skip, limit=per_page)
        total = await self._repository.count()
        return items, total

    async def get_by_id(self, id: str) -> User | None:
        """Kullanıcı detayını getirir."""
        return await self._repository.find_by_id(id)
