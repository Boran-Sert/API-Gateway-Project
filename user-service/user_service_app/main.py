from fastapi import FastAPI, Depends, Header
from dotenv import load_dotenv
load_dotenv()
from user_service_app.services.user_service import UserService
from user_service_app.models.user import UserUpdate
from user_service_app.db import lifespan
from user_service_app.repositories.user_repository import UserRepository
from shared.exceptions import AppException, app_exception_handler
from shared.logging import setup_logging
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics
app = FastAPI(title="User Service", version="1.0.0", lifespan=lifespan)
logger = setup_logging("user-service")
app.add_exception_handler(AppException, app_exception_handler)
setup_metrics(app, "user-service")
app.add_middleware(LoggingMiddleware, logger=logger)
def get_user_repository():
    return UserRepository()
def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repository=repo)
async def get_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    """Gateway'den gelen X-User-ID başlığını alır."""
    return x_user_id
async def get_user_email(x_user_email: str = Header(..., alias="X-User-Email")) -> str:
    """Gateway'den gelen X-User-Email başlığını alır."""
    return x_user_email
@app.get("/me", summary="Kullanıcının kendi profilini getirir")
async def get_my_profile(
    user_id: str = Depends(get_user_id),
    user_email: str = Depends(get_user_email),
    service: UserService = Depends(get_user_service),
):
    return await service.get_my_profile(user_id, user_email)
@app.put("/me", summary="Kullanıcının kendi profilini günceller")
async def update_my_profile(
    user_data: UserUpdate,
    user_id: str = Depends(get_user_id),
    user_email: str = Depends(get_user_email),
    service: UserService = Depends(get_user_service),
):
    return await service.update_my_profile(user_id, user_email, user_data)
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "user-service"}