"""Veri erişim katmanı — Abstract Repository ve MongoDB """

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection

T = TypeVar("T", bound=BaseModel)

class AbstarctRepository(ABC, Generic[T]):
    """Soyut Repository — tüm veri erişim sınıflarının arayüzü.
    
    SOLID Prensipleri:
      - Interface Segregation: Yalnızca CRUD operasyonları tanımlı
      - Dependency Inversion: Service katmanı bu arayüze bağımlıdır, 
        somut MongoDB değil
    """
    @abstractmethod
    async def find_by_id(self, id: str) -> T | None: ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[T]: ...

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def create(self, entity: T) -> T: ...

    @abstractmethod
    async def uptade(self, id: str, entity: T) -> T | None: ...

    @abstractmethod
    async def delete(self, id: str) -> bool: ...


class MongoRepository(AbstarctRepository[T]):
    """MongoDB implementasyonu — Motor async driver.
    
    SOLID Prensipleri:
      - Liskov Substitution: AbstractRepository yerine kullanılabilir
      - Single Responsibility: Yalnızca MongoDB CRUD işlemleri
    """
    def __init__(self, collection: AsyncIOMotorCollection, model_class: type[T]):
        self._collection = collection
        self._model_class = model_class
    
    async def find_by_id(self, id: str) -> T | None:
        doc = await self._collection.find_one({"_id": id})
        return self._model_class(**doc) if doc else None
    
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[T]:
        cursor = self._collection.find().skip(skip).limit(limit)
        return [self._model_class(**doc) async for doc in cursor]

    async def count(self) -> int:
        return await self._collection.count_documents({})
    async def create(self, entity: T) -> T:
        doc = entity.model_dump(by_alias=True)
        await self._collection.insert_one(doc)
        return entity

    async def update(self, id: str, entity: T) -> T | None:
        result = await self._collection.update_one(
            {"_id": id}, {"$set": entity.model_dump(exclude={"id"}, by_alias=True)}
        )
        return entity if result.modified_count else None

    async def delete(self, id: str) -> bool:
        result = await self._collection.delete_one({"_id": id})
        return result.deleted_count > 0



