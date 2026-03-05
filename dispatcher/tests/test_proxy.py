""" Porxy Testleri """

from fastapi.testclient import TestClient
from dispatcher.app.main import app

client = TestClient(app)

def test_dispatcher_health_returns_200():
    """ /health endpoint 200 döndürmeli sistem ayakta """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dispatcher"}

def test_dispatcher_routes_request_to_user_service():
    """ /api/users isteği user-service'e yönlendirilmeli. """
    reponse = client.get("api/users")
    assert reponse.status_code == 200
