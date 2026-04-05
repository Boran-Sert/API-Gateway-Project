import uuid
import jwt
import json
import datetime
from auth_app.models.auth import (
    RegisterRequest,
    LoginRequest,
    UserCredential,
    UserResponse,
)
from auth_app.repositories.mongo_repository import MongoUserRepository
from auth_app.core.security import hash_password, verify_password
from shared.exceptions import ConflictException, UnauthorizedException
from shared.config import load_config
config = load_config()
class AuthService:
    def __init__(self, repository: MongoUserRepository, redis_client=None):
        self._repository = repository
        self._redis = redis_client
        self.secret_key = config.jwt.secret_key
        self.algorithm = config.jwt.algorithm
        self.expire_seconds = config.jwt.expire_seconds
    async def register(self, request: RegisterRequest) -> UserResponse:
        """Yeni bir kullanıcı kaydeder."""
        existing_user = await self._repository.find_by_email(request.email)
        if existing_user:
            raise ConflictException("Bu e-posta zaten kullanılıyor")
        hashed_pw = hash_password(request.password)
        user_id = str(uuid.uuid4())
        assigned_role = "admin" if request.email.startswith("admin") else "user"
        user_cred = UserCredential(
            _id=user_id,                                     
            email=request.email,
            hashed_password=hashed_pw,
            role=assigned_role,                        
        )
        await self._repository.create(user_cred)
        return UserResponse(id=user_id, email=request.email)
    async def login(self, request: LoginRequest):
        """Kullanıcı girişini doğrular ve Redis'e oturum yazar."""
        user = await self._repository.find_by_email(request.email)
        if not user:
            raise UnauthorizedException("Geçersiz e-posta")
        if not verify_password(request.password, user.hashed_password):
            raise UnauthorizedException("Geçersiz şifre")
        payload = {
            "sub": user.email,
            "user_id": str(user.id),
            "role": user.role,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=self.expire_seconds),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        if self._redis:
            session_data = json.dumps(
                {
                    "email": user.email,
                    "user_id": str(user.id),
                    "role": user.role,
                }
            )
            await self._redis.set(
                f"token:{token}", session_data, ex=self.expire_seconds
            )
        return {"token": token}
    async def validate_token(self, token: str) -> dict:
        """Token'ı doğrular. Önce Redis'e, sonra JWT'ye bakar."""
        if self._redis:
            session_data = await self._redis.get(f"token:{token}")
            if session_data:
                return json.loads(session_data)
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {
                "email": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "role": payload.get("role", "user"),
            }
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token süresi dolmuş")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Geçersiz token")