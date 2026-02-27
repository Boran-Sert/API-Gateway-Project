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


class MongoRepository(AbstractRepository[T]):
    """MongoDB implementasyonu — Motor async driver.
    
    SOLID Prensipleri:
      - Liskov Substitution: AbstractRepository yerine kullanılabilir
      - Single Responsibility: Yalnızca MongoDB CRUD işlemleri
    """




