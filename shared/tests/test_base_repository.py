""" Repository Katmanı Testleri"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from shared.base_repository import AbstractRepository, MongoRepository
from pydantic import BaseModel

# --- Test için Pydantic Model ---
class FakeUser(BaseModel):
    id: str
    name: str

# --- AbstractRepository Testleri ---
def test_abstract_repository_cannot_be_instantiated():
    """ Soyut sınıfı doğrudan oluşturulamamalı"""
    with pytest.raises(TypeError):
        AbstractRepository()

# --- MongoRepository Testleri ---
@pytest.fixture
def mock_collection():
    """ Sahte MongoDB collection oluşturur"""
    collection = MagicMock()
    collection.find_one = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()
    return collection

@pytest.fixture
def repo(mock_collection):
    """ Test için MongoRepository örneği """
    return MongoRepository(collection=mock_collection, model_class=FakeUser)


@pytest.mark.asyncio
async def test_find_by_id_returns_model_when_found(repo, mock_collection):
    """ Kayıt bulunduğunda Pydantic modeli döndürmeli """
    mock_collection.find_one.return_value = {"_id": "1", "id": "1", "name": "Boran"}
    result = await repo.find_by_id("1")
    assert result is not None
    assert result.name == "Boran"


@pytest.mark.asyncio
async def test_find_by_id_returns_none_when_not_found(repo, mock_collection):
    """Kayıt bulunamadığında None döndürmeli."""
    mock_collection.find_one.return_value = None
    result = await repo.find_by_id("999")
    assert result is None


@pytest.mark.asyncio
async def test_create_calls_insert_one(repo, mock_collection):
    """create() çağrıldığında MongoDB insert_one tetiklenmeli."""
    user = FakeUser(id="1", name="Boran")
    result = await repo.create(user)
    mock_collection.insert_one.assert_called_once()
    assert result.name == "Boran"


@pytest.mark.asyncio
async def test_delete_returns_true_when_deleted(repo, mock_collection):
    """Silme başarılıysa True dönmeli."""
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    result = await repo.delete("1")
    assert result is True


@pytest.mark.asyncio
async def test_delete_returns_false_when_not_found(repo, mock_collection):
    """Silinecek kayıt yoksa False dönmeli."""
    mock_collection.delete_one.return_value = MagicMock(deleted_count=0)
    result = await repo.delete("999")
    assert result is False


@pytest.mark.asyncio
async def test_count_returns_document_count(repo, mock_collection):
    """count() doğru sayıyı döndürmeli."""
    mock_collection.count_documents.return_value = 42
    result = await repo.count()
    assert result == 42