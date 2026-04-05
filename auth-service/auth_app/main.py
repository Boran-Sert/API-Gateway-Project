from fastapi import FastAPI
import os
from dotenv import load_dotenv
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
load_dotenv()
from auth_app.services.auth_service import AuthService
from auth_app.repositories.mongo_repository import MongoUserRepository
from motor.motor_asyncio import AsyncIOMotorClient
from shared.exceptions import AppException, app_exception_handler
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics
from shared.logging import setup_logging
from auth_app.api.router import router 
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-auth:27017")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client.get_database("auth_db")
    user_collection = db.get_collection("credentials")
    repo = MongoUserRepository(user_collection)
    redis_conn = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", 
        decode_responses=True
    )
    app.state.auth_service = AuthService(repository=repo, redis_client=redis_conn)
    yield                                     
    await redis_conn.close()
    mongo_client.close()
app = FastAPI(
    title="Auth Service", 
    version="1.0.0",
    lifespan=lifespan
)
logger = setup_logging("auth-service")
app.add_exception_handler(AppException, app_exception_handler)
app.add_middleware(LoggingMiddleware, logger=logger)
setup_metrics(app, service_name="auth-service")
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth-service"}
app.include_router(router)