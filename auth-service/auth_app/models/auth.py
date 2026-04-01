from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class UserCredential(BaseModel):
    """Veritabanında tutulacak kimlik bilgisi modeli."""
    # MongoDB'den gelen _id'yi 'id' olarak kullanmamızı sağlar
    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str

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
    """Başarılı işlem sonrası dönülecek kullanıcı bilgisi."""
    id: str = Field(alias="_id")
    email: EmailStr
    
    model_config = ConfigDict(populate_by_name=True)