from fastapi.testclient import TestClient

# Bilerek hata verdirtiyoruz çünkü henüz uygulamayı yazmadık (TDD Red Aşaması)
try:
    from app.main import app
    client = TestClient(app)
except ImportError:
    client = None

def test_get_empty_products_list():
    """
    Sistemde hiç ürün yokken GET /products isteğinin testi.
    """
    assert client is not None, "Uygulama (app.main) henüz yok!"
    
    response = client.get("/products")
    
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    
    # RMM Seviye 3 HATEOAS kontrolü
    assert "_links" in json_data
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"] == "/products"