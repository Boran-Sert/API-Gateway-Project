from pydantic import BaseModel, EmailStr, Field

class UserCredential(BaseModel):
    """Veritabanında tutulacak kimlik bilgisi modeli."""
    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str

class LoginRequest(BaseModel):
    """Giriş isteği şeması."""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Kayıt isteği şeması."""
    email: EmailStr
    password: str
