""" Kimlik doğrulama işlemlerinin HTTP arayüzleri  """
from fastapi import APIRouter, HTTPException, status, Depends
from auth_app.models.auth import RegisterRequest, LoginRequest, UserResponse
from auth_app.services.auth_service import AuthService
from auth_app.repositories.mongo_repository import MongoUserRepository
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/auth", tags=["auth"])
MONGO_URL = os.getenv("MONGO_AUTH_URL", "mongodb://mongo-auth:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.auth_db
collection = db.credentials

def get_auth_service() -> AuthService:
    repo = MongoUserRepository(collection=collection)
    return AuthService(repository=repo)

# --- Endpoint'ler ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
        """ Kullanıcı kaydı """
        user = await service.register(request)
        return user
@router.post("/login")
async def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
        """
        Kullanıcı girişi.
        """
        result = await service.login(request) 
        return result