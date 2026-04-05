"""shared/config.py modülü için birim testleri."""
import os
import pytest
import tempfile
import yaml
from pathlib import Path
from shared.config import (
    AppConfig,
    JWTConfig,
    RedisConfig,
    MongoConfig,
    ServiceConfig,
    load_config,
)
class TestJWTConfig:
    """JWT konfigürasyon testleri."""
    def test_default_values(self):
        cfg = JWTConfig()
        assert cfg.secret_key == "change-this-in-production"
        assert cfg.algorithm == "HS256"
        assert cfg.expire_seconds == 3600
    def test_custom_values(self):
        cfg = JWTConfig(secret_key="my-secret", algorithm="HS512", expire_seconds=7200)
        assert cfg.secret_key == "my-secret"
        assert cfg.algorithm == "HS512"
        assert cfg.expire_seconds == 7200
class TestRedisConfig:
    """Redis konfigürasyon testleri."""
    def test_default_url(self):
        cfg = RedisConfig()
        assert cfg.url == "redis://redis-cache:6379"
    def test_custom_url(self):
        cfg = RedisConfig(host="localhost", port=6380)
        assert cfg.url == "redis://localhost:6380"
class TestLoadConfig:
    """load_config fonksiyonu testleri."""
    def test_load_defaults_without_file(self, monkeypatch):
        """Dosya verilmezse varsayılan değerler kullanılmalı."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("REDIS_HOST", raising=False)
        monkeypatch.delenv("REDIS_PORT", raising=False)
        cfg = load_config()
        assert isinstance(cfg, AppConfig)
        assert cfg.jwt.algorithm == "HS256"
    def test_load_from_yaml(self, tmp_path, monkeypatch):
        """YAML dosyasından değer yüklenebilmeli."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("REDIS_HOST", raising=False)
        monkeypatch.delenv("REDIS_PORT", raising=False)
        yaml_data = {
            "jwt": {"secret_key": "yaml-secret", "expire_seconds": 1800},
            "redis": {"host": "my-redis", "port": 6380},
        }
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(yaml_data), encoding="utf-8")
        cfg = load_config(yaml_file)
        assert cfg.jwt.secret_key == "yaml-secret"
        assert cfg.jwt.expire_seconds == 1800
        assert cfg.redis.host == "my-redis"
    def test_env_overrides_yaml(self, tmp_path, monkeypatch):
        """Ortam değişkenleri YAML değerlerini ezmeli."""
        yaml_data = {"jwt": {"secret_key": "yaml-secret"}}
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(yaml_data), encoding="utf-8")
        monkeypatch.setenv("SECRET_KEY", "env-secret")
        cfg = load_config(yaml_file)
        assert cfg.jwt.secret_key == "env-secret"
    def test_nonexistent_file_uses_defaults(self, monkeypatch):
        """Var olmayan dosya yolu verilirse varsayılanlar kullanılmalı."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("REDIS_HOST", raising=False)
        monkeypatch.delenv("REDIS_PORT", raising=False)
        cfg = load_config("/nonexistent/path/config.yaml")
        assert isinstance(cfg, AppConfig)
        assert cfg.jwt.secret_key == "change-this-in-production"