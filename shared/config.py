"""Merkezi konfigürasyon yönetimi — YAML + Pydantic tabanlı."""
import os
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
class JWTConfig(BaseModel):
    """JWT token ayarları."""
    secret_key: str = Field(default="change-this-in-production")
    algorithm: str = Field(default="HS256")
    expire_seconds: int = Field(default=3600)
class RedisConfig(BaseModel):
    """Redis bağlantı ayarları."""
    host: str = Field(default="redis-cache")
    port: int = Field(default=6379)
    decode_responses: bool = Field(default=True)
    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"
class MongoConfig(BaseModel):
    """MongoDB bağlantı ayarları."""
    url: str = Field(default="mongodb://localhost:27017")
    db_name: str = Field(default="app_db")
class ServiceConfig(BaseModel):
    """Tek bir mikroservisin konfigürasyonu."""
    name: str
    url: Optional[str] = None
    mongo: MongoConfig = Field(default_factory=MongoConfig)
    redis: Optional[RedisConfig] = None
    jwt: Optional[JWTConfig] = None
class AppConfig(BaseModel):
    """Uygulamanın tüm ayarlarını tutan kök konfigürasyon sınıfı."""
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    services: dict[str, ServiceConfig] = Field(default_factory=dict)
def load_config(config_path: str | Path | None = None) -> AppConfig:
    """
    Konfigürasyonu yükler.
    Öncelik sırası:
    1. Ortam değişkenleri (ENV) → her zaman üzerine yazar.
    2. YAML dosyası → temel değerleri sağlar.
    3. Varsayılan değerler → hiçbir şey yoksa kullanılır.
    """
    config_data: dict = {}
    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
    env_secret = os.getenv("SECRET_KEY")
    env_redis_host = os.getenv("REDIS_HOST")
    env_redis_port = os.getenv("REDIS_PORT")
    if env_secret:
        config_data.setdefault("jwt", {})["secret_key"] = env_secret
    if env_redis_host:
        config_data.setdefault("redis", {})["host"] = env_redis_host
    if env_redis_port:
        config_data.setdefault("redis", {})["port"] = int(env_redis_port)
    return AppConfig(**config_data)