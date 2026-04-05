import os
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "product_db"
client: AsyncIOMotorClient = None
def get_database() -> AsyncIOMotorClient:
    """Veritabanı bağlantısını döndürür."""
    return client[DB_NAME]
@asynccontextmanager
async def lifespan(app):
    """Uygulama yaşam döngüsü boyunca veritabanı bağlantısını yönetir."""
    global client
    client = AsyncIOMotorClient(MONGO_URL)
    yield
    client.close()