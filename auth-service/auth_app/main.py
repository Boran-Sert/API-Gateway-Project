from fastapi import FastAPI
import os
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

from auth_app.services.auth_service import AuthService
from auth_app.repositories.mongo_repository import MongoUserRepository
from motor.motor_asyncio import AsyncIOMotorClient

# --- Paylaşılan kütüphaneler ---
from shared.exceptions import AppException, app_exception_handler
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics
from shared.logging import setup_logging
from auth_app.api.router import router 

# --- BAĞLANTI AYARLARI ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-auth:27017")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --- LIFESPAN (Modern Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. MongoDB Bağlantısını Kur
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client.get_database("auth_db")
    
    # 2. KRİTİK DÜZELTME: Koleksiyonu açıkça alıyoruz
    # Hata aldığın yer burasıydı, repo artık direkt Motor koleksiyonunu alacak
    user_collection = db.get_collection("credentials")
    repo = MongoUserRepository(user_collection)
    
    # 3. Redis Bağlantısı (Async)
    redis_conn = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", 
        decode_responses=True
    )
    
    # 4. AuthService Başlat ve State'e ekle
    app.state.auth_service = AuthService(repository=repo, redis_client=redis_conn)
    
    yield  # Uygulama çalışırken burası bekler
    
    # 5. Kapanışta bağlantıları temizle (Opsiyonel ama iyi uygulama)
    await redis_conn.close()
    mongo_client.close()

# FastAPI Uygulaması
app = FastAPI(
    title="Auth Service", 
    version="1.0.0",
    lifespan=lifespan
)

# Servise özel logger'ı başlat
logger = setup_logging("auth-service")

# Exception Handler ve Middleware
app.add_exception_handler(AppException, app_exception_handler)
app.add_middleware(LoggingMiddleware, logger=logger)
setup_metrics(app, service_name="auth-service")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth-service"}

app.include_router(router)