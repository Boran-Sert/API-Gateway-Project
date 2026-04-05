""" Kimlik doğrulama işlemlerinin HTTP arayüzleri  """
from fastapi import APIRouter, status, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_app.models.auth import RegisterRequest, LoginRequest
from auth_app.services.auth_service import AuthService
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
def get_auth_service(req: Request) -> AuthService:
    """Uygulama state'inden AuthService'i alır."""
    return req.app.state.auth_service
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    """ Kullanıcı kaydı """
    user = await service.register(request)
    return user
@router.post("/login")
async def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """ Kullanıcı girişi """
    return await service.login(request)
@router.post("/validate")
async def validate(credentials: HTTPAuthorizationCredentials = Security(security), service: AuthService = Depends(get_auth_service)):
    """ Token doğrulama ve kullanıcı bilgilerini çözme """
    return await service.validate_token(credentials.credentials)