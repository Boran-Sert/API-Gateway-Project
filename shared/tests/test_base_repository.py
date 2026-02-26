""" Repository Katmanı Testleri"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from shared.base_repository import AbstractRepository, MongoRepository
from pydantic import BaseModel