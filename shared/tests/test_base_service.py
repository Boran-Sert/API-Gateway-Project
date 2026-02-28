""" Base Service Katmanı Testleri"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel
from shared.base_service import AbstractService
from shared.base_repository import AbstractRepository

# --- Test için FakeUser --- #
class FakeUser(BaseModel):
    id: str
    name: str

# --- Abstarct Service doğrudan oluşturulamamalı --- #

def test_abstract_service_cannot_be_instantiated():
    """ Soyut sınıfı doğrudan oluşmamalı """
    with pytest.raises(TypeError):

        AbstractService(repository=MagicMock())


class ConcreteService(AbstractService):
    """Test için AbstractService'i implement eden somut sınıf."""
    async def get_by_id(self, id: str):
        return await self._repository.find_by_id(id)
    async def get_all(self, page: int, per_page: int):
        skip = (page - 1) * per_page
        items = await self._repository.find_all(skip=skip, limit=per_page)
        total = await self._repository.count()
        return items, total


@pytest.fixture
def mock_repo():
    """Sahte repository oluşturur."""
    repo = MagicMock()
    repo.find_by_id = AsyncMock()
    repo.find_all = AsyncMock()
    repo.count = AsyncMock()
    return repo

@pytest.fixture
def service(mock_repo):
    """Test için somut service örneği."""
    return ConcreteService(repository=mock_repo)

@pytest.mark.asyncio
async def test_service_stores_repository(mock_repo):
    """Service, verilen repository'yi saklamalı."""
    svc = ConcreteService(repository=mock_repo)
    assert svc._repository is mock_repo

@pytest.mark.asyncio
async def test_get_by_id_delegates_to_repository(service, mock_repo):
    """get_by_id çağrısı repository'ye aktarılmalı."""
    mock_repo.find_by_id.return_value = FakeUser(id="1", name="Boran")
    result = await service.get_by_id("1")
    mock_repo.find_by_id.assert_called_once_with("1")
    assert result.name == "Boran"

@pytest.mark.asyncio
async def test_get_all_calculates_skip_correctly(service, mock_repo):
    """Sayfa 2, per_page 10 ise skip=10 olmalı."""
    mock_repo.find_all.return_value = []
    mock_repo.count.return_value = 0
    await service.get_all(page=2, per_page=10)
    mock_repo.find_all.assert_called_once_with(skip=10, limit=10)
