from fastapi import FastAPI, Depends, Header
from user_service_app.services.user_service import UserService
from user_service_app.models.user import UserUpdate
from user_service_app.db import lifespan
from shared.exceptions import AppException, app_exception_handler
from shared.logging import setup_logging
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics

app = FastAPI(
    title="User Service",
    version="1.0.0",
    lifespan=lifespan
)

# Servise özel logger'ı başlat
logger = setup_logging("user-service")

# Hata yakalama mekanizmasını ekle
app.add_exception_handler(AppException, app_exception_handler)

# Prometheus metriklerini ayarla
setup_metrics(app, "user-service")

# Loglama middleware'ini logger ile birlikte ekle
app.add_middleware(LoggingMiddleware, logger=logger)

# Dependency Injection
def get_user_service():
    return UserService()

# Header Dependencies
async def get_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    """Gateway'den gelen X-User-ID başlığını alır."""
    return x_user_id

async def get_user_email(x_user_email: str = Header(..., alias="X-User-Email")) -> str:
    """Gateway'den gelen X-User-Email başlığını alır."""
    return x_user_email

@app.get("/users/me", summary="Kullanıcının kendi profilini getirir")
async def get_my_profile(
    user_id: str = Depends(get_user_id),
    user_email: str = Depends(get_user_email),
    service: UserService = Depends(get_user_service)
):
    """Giriş yapmış kullanıcının profil bilgilerini getirir."""
    return await service.get_my_profile(user_id, user_email)

@app.put("/users/me", summary="Kullanıcının kendi profilini günceller")
async def update_my_profile(
    user_data: UserUpdate,
    user_id: str = Depends(get_user_id),
    user_email: str = Depends(get_user_email),
    service: UserService = Depends(get_user_service)
):
    """Giriş yapmış kullanıcının profil bilgilerini günceller."""
    return await service.update_my_profile(user_id, user_email, user_data)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "user-service"}