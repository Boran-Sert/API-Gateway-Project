""" Auth Service """

import uuid
from app.models.auth import RegisterRequest, LoginRequest, UserCredential, UserResponse
from app.repositories.mongo_repository import MongoUserRepository
from app.core.security import hash_password, verify_password
from shared.exceptions import ConflictException, UnauthorizedException
import jwt
import datetime

class AuthService:
    SECRET_KEY = "22042507012004" 
    def __init__(self,repository: MongoUserRepository):
        self._repository = repository

    async def register(self, request: RegisterRequest) -> UserResponse:
        """
        Yeni bir kullanıcı kaydeder.
        1. E-posta kullanımda mı kontrol et.
        2. Şifreyi hash'le.
        3. Veritabanına kaydet.
        """

        #1 E-posta kontrolü
        existing_user = await self._repository.find_by_email(request.email)
        if existing_user:
            raise ConflictException(
              "Bu e-posta zaten kullanılıyor"
            )

        #2 Şifreyi hashle
        hassed_password = hash_password(request.password)

        #3 Veritabanına kaydet
        user_id = str(uuid.uuid4())
        user_cred = UserCredential(
            _id = user_id,
            email = request.email,
            hashed_password = hassed_password
        )
        
        # 4. Kaydet
        await self._repository.create(user_cred)

        # 5. Response modeline dönüştürerek döndür
        return UserResponse(_id=user_id, email=request.email)

    async def login(self, request: LoginRequest):
        """
        Kullanıcı girişini doğrular.
        """
        #1 kullanıcıyı bul
        user = await self._repository.find_by_email(request.email)

        if not user:
            raise UnauthorizedException(
                "Geçersiz e-posta"
            )
        
        # 2. Şifreyi doğrula
        if not verify_password(request.password, user.hashed_password):
            raise UnauthorizedException(
                "Geçersiz şifre"
            )

        # 3. JWT üğret
        payload ={
            "sub": user.email,
            "exp": datetime.datetime.utcnow + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        return {"token": token}
        