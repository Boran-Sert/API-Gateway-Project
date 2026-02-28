"""İş mantığı katmanı — Abstract Service arayüzü"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel
from shared.base_repository import AbstractRepository

T = TypeVar("T", bound=BaseModel)

class AbstractService(ABC ,Generic[T]):
    """ Soyut Service — iş mantığı katmanı arayüzü. """

    def __init__(self, repository: AbstractRepository[T]):
        """ Servisi bağlı oldığu Repository ile başlatır """

        self._repository = repository
    
    @abstractmethod
    async def get_all(self, page: int, per_page: int) -> tuple[list[T], int]:
        """ Kayıtları sayfalı şekilde döndür (items, total) olarak döner """
        ...
    
    @abstractmethod
    async def get_by_id(self, id: str) -> T:
        """ Tek bir kaydı id ile döndürür """
        ...
