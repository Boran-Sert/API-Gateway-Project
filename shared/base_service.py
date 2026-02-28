"""Servis katmanı — Abstract Service tanımı"""

from abc import ABC, abstractmethod
from shared.base_repository import AbstractRepository


class AbstractService(ABC):
    """Tüm servis sınıflarının miras alacağı soyut temel sınıf."""

    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    @abstractmethod
    async def get_by_id(self, id: str):
        """Tek kayıt getirir."""
        ...

    @abstractmethod
    async def get_all(self, page: int, per_page: int):
        """Tüm kayıtları sayfalı getirir."""
        ...
