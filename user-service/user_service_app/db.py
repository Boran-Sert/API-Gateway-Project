from motor.motor_asyncio import AsyncIOMotorClient
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-user:27017")
client = AsyncIOMotorClient(MONGO_URL)
def get_database():
    return client.user_db
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    collections = await db.list_collection_names()
    if "users" not in collections:
        await db.users.create_index("email", unique=True)
        print("INFO: 'users' collection initialized automatically.")
    yield
    client.close()