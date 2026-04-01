import uuid
import jwt
import json
import datetime
from auth_app.models.auth import RegisterRequest, LoginRequest, UserCredential, UserResponse
from auth_app.repositories.mongo_repository import MongoUserRepository
from auth_app.core.security import hash_password, verify_password
from shared.exceptions import ConflictException, UnauthorizedException

class AuthService:
    SECRET_KEY = "22042507012004" 

    def __init__(self, repository: MongoUserRepository, redis_client=None):
        self._repository = repository
        self._redis = redis_client

    async def register(self, request: RegisterRequest) -> UserResponse:
        """Yeni bir kullanıcı kaydeder."""
        # 1. E-posta kontrolü
        existing_user = await self._repository.find_by_email(request.email)
        if existing_user:
            raise ConflictException("Bu e-posta zaten kullanılıyor")

        # 2. Şifreyi hashle
        hashed_pw = hash_password(request.password)

        # 3. Veritabanına kaydet
        user_id = str(uuid.uuid4())
        user_cred = UserCredential(
            _id=user_id, # Alias sayesinde _id olarak atanır
            email=request.email,
            hashed_password=hashed_pw
        )
        
        await self._repository.create(user_cred)

        # 4. Response modeline dönüştürerek döndür
        return UserResponse(id=user_id, email=request.email)

    async def login(self, request: LoginRequest):
        """Kullanıcı girişini doğrular ve Redis'e oturum yazar."""
        # 1. Kullanıcıyı bul
        user = await self._repository.find_by_email(request.email)

        if not user:
            raise UnauthorizedException("Geçersiz e-posta")
        
        # 2. Şifreyi doğrula
        if not verify_password(request.password, user.hashed_password):
            raise UnauthorizedException("Geçersiz şifre")

        # 3. JWT üret
        payload = {
            "sub": user.email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        
        # 4. Redis'e JSON formatında kaydet
        if self._redis:
            # KRİTİK DÜZELTME: user._id yerine user.id kullanıyoruz (Alias sayesinde)
            session_data = json.dumps({
                "email": user.email,
                "user_id": str(user.id) 
            })
            # f-string içinde token'ı anahtar olarak kullanıyoruz
            await self._redis.set(f"token:{token}", session_data, ex=3600)
            
        return {"token": token}