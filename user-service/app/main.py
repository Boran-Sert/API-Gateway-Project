from fastapi import FastAPI, Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient
import os

from shared.exceptions import AppException, app_exception_handler
from shared.middleware import RequestLoggingMiddleware
from shared.metrics import setup_metrics
from shared.hateoas import HateoasBuilder

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

app = FastAPI(title="User Service", version="1.0.0")

# Faz 1: Shared Library Entegrasyonu
app.add_exception_handler(AppException, app_exception_handler)
app.add_middleware(RequestLoggingMiddleware)
setup_metrics(app, service_name="user-service")

# Veri tabanı bağlantısı
MONGO_URL = os.getenv("MONGO_URL", "mongodb://user-mongo:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.user_db
collection = db.users

# Dependency Injection (Bağımlılık Enjeksiyonu)
def get_user_service() -> UserService:
    repo = UserRepository(collection=collection, model_class=User)
    return UserService(repository=repo)


@app.get("/users")
async def get_users(request: Request, page: int = 1, per_page: int = 10, service: UserService = Depends(get_user_service)):
    """
    Kullanıcı listesini getirir (Faz 4 OOM Kurallarıyla).
    """
    users, total = await service.get_all(page, per_page)
    
    # HATEOAS Mimarisi (Faz 1 shared kütüphanesi kullanımı)
    builder = HateoasBuilder(base_url="")
    
    serialized_users = [u.model_dump(by_alias=True) for u in users]
    
    return builder.collection_response(
        items=serialized_users,
        resource_name="users",
        page=page,
        per_page=per_page,
        total=total
    )