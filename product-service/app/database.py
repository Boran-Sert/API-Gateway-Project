import os
from motor.motor_asyncio import AsyncIOMotorClient

# Docker ile çalışırken MONGO_URL kullanılacak, yoksa localhost.
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URL)

# Sadece bu servise özel veritabanı
db = client.product_db