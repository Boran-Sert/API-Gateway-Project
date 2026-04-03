from pydantic import BaseModel, EmailStr, Field, ConfigDict



class UserCredential(BaseModel):
    """Veritabanında tutulacak kimlik bilgisi modeli."""

    # MongoDB'den gelen _id'yi 'id' olarak kullanmamızı sağlar
    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str
    role: str = "user"

    # Pydantic V2 için modern konfigürasyon
    model_config = ConfigDict(populate_by_name=True)


class LoginRequest(BaseModel):
    """Giriş isteği şeması."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Kayıt isteği şeması."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Başarılı işlem sonrası dönülecek kullanıcı bilgisi (API Response DTO)."""

    id: str
    email: EmailStr

