from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import uuid4

class UserBase(BaseModel):
    """Kullanıcı profilinin güncellenebilir alanlarını tanımlar."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Kullanıcı adı")
    full_name: Optional[str] = Field(None, max_length=100, description="Tam ad")
    bio: Optional[str] = Field(None, max_length=250, description="Kullanıcı biyografisi")
    profile_image_url: Optional[str] = Field(None, description="Profil fotoğrafı URL'si")

class UserUpdate(BaseModel):
    """Profil güncelleme isteği için kullanılan model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Kullanıcı adı")
    full_name: Optional[str] = Field(None, max_length=100, description="Tam ad")
    bio: Optional[str] = Field(None, max_length=250, description="Kullanıcı biyografisi")
    profile_image_url: Optional[str] = Field(None, description="Profil fotoğrafı URL'si")

class User(UserBase):
    """Veritabanında saklanan tam kullanıcı profili modeli."""
    id: str = Field(
        default_factory=lambda: str(uuid4()), 
        alias="_id", 
        description="Kullanıcının benzersiz ID'si (Auth Service'ten gelen ID ile aynı)"
    )
    email: EmailStr = Field(..., description="Kullanıcının e-posta adresi (değiştirilemez)")

    class Config:
        populate_by_name = True