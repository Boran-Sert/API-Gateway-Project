"""Veri erişim katmanı — Abstract Repository ve MongoDB """

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection

T = TypeVar("T", bound=BaseModel)

class AbstractRepository(ABC, Generic[T]):
    """Soyut Repository — tüm veri erişim sınıflarının arayüzü."""
    
    @abstractmethod
    async def find_by_id(self, id: str) -> T | None:
        """Verilen ID'ye sahip kaydı getirir. Bulunamazsa None döner."""  
        ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[T]:
        """Kayıtları sayfalı şekilde listeler. skip: atlanacak, limit: max kayıt."""  
        ...

    @abstractmethod
    async def count(self) -> int:
        """Koleksiyondaki toplam kayıt sayısını döner."""  
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Yeni kayıt oluşturur ve oluşturulan kaydı döner."""  
        ...

    @abstractmethod
    async def update(self, id: str, entity: T) -> T | None:
        """Mevcut kaydı günceller. Kayıt yoksa None döner."""  
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Kaydı siler. Başarılıysa True, bulunamazsa False döner."""  
        ...


class MongoRepository(AbstractRepository[T]):
    """MongoDB implementasyonu — Motor async driver."""
    
    def __init__(self, collection: AsyncIOMotorCollection, model_class: type[T]):
        """Koleksiyon bağlantısı ve model sınıfı ile başlatır."""
        self._collection = collection
        self._model_class = model_class
    
    async def find_by_id(self, id: str) -> T | None:
        """MongoDB'den _id ile tek kayıt sorgular."""
        doc = await self._collection.find_one({"_id": id})
        return self._model_class(**doc) if doc else None
    
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[T]:
        """Tüm kayıtları sayfalayarak getirir."""
        cursor = self._collection.find().skip(skip).limit(limit)
        return [self._model_class(**doc) async for doc in cursor]

    async def count(self) -> int:
        """Koleksiyondaki toplam doküman sayısını döner."""
        return await self._collection.count_documents({})
    
    async def create(self, entity: T) -> T:
        """Yeni doküman ekler ve eklenen entity'yi döner."""
        doc = entity.model_dump(by_alias=True)
        await self._collection.insert_one(doc)
        return entity

    async def update(self, id: str, entity: T) -> T | None:
        """Mevcut dokümanı günceller. Değişiklik yoksa None döner."""
        result = await self._collection.update_one(
            {"_id": id}, {"$set": entity.model_dump(exclude={"id"}, by_alias=True)}
        )
        return entity if result.modified_count else None

    async def delete(self, id: str) -> bool:
        """Dokümanı siler. Silindiyse True, bulunamadıysa False döner."""
        result = await self._collection.delete_one({"_id": id})
        return result.deleted_count > 0



