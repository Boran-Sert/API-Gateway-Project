""" User Service API Testleri """

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users_returns_hateoas_format():
    """/users endpoint'inin HATEOAS (_links) yapısında dönmesini test eder."""

    response = client.get("/users")

    # HTTP 200 dönmeli
    assert response.status_code == 200

    # Cevabın içinde HATEOAS için _links olmlaı ve asıl veri data içinde olmalı
    json_data = response.json()
    assert "data" in json_data
    assert "_links" in json_data

    # kendi kendine self linkine sahip olmalı
    assert "self" in json_data["_links"]
    assert "json_data"["_links"]["self"]["href"] == "/users"