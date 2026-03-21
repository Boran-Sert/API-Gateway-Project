from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    """Kullanıcı modelimiz (Pydantic ile doğrulama)"""
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    is_active: bool = True
