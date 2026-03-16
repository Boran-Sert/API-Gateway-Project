from motor.motor_asyncio import AsyncIOMotorCollection
from shared.base_repository import MongoRepository
from app.models.auth import UserCredential

class MongoUserRepository(MongoRepository[UserCredential]):
    """Kimlik doğrulama işlemleri için MongoDB repository """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, UserCredential)
    
    async def find_by_email(self, email: str) -> UserCredential | None:
        """E-posta adresine göre kullanıcıyı bulur."""
        doc = await self._collection.find_one({"email": email})
        return UserCredential(**doc) if doc else None
