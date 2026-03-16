""" Kimlik doğrulama işlemlerinin HTTP arayüzleri  """

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.auth_service import AuthService
from app.repositories.mongo_repository import MongoUserRepository