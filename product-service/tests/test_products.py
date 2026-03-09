from fastapi.testclient import TestClient

# Bilerek hata verdirtiyoruz çünkü henüz uygulamayı henuz yazmadık
try:
    from app.main import app
    client = TestClient(app)
except ImportError:
    client = None

def test_get_empty_products_list():
    """
    Sistemde hiç ürün yokken GET /products isteğinin testi.
    Boş bir liste ve HATEOAS linkleri dönmelidir.
    """
    assert client is not None, "Uygulama (app.main) henüz yok"
    
    response = client.get("/products")
    
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    
    assert "_links" in json_data
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"] == "/products"

def test_create_product():
    """
    Yeni ürün ekleme testi (POST /products).
    """
    new_product = {
        "name": "Mekanik Klavye",
        "price": 1250.00,
        "category": "Elektronik",
        "stock": 50
    }
    
    response = client.post("/products", json=new_product)
    
    assert response.status_code == 201
    
    json_data = response.json()
    assert json_data["data"]["name"] == "Mekanik Klavye"
    assert json_data["data"]["price"] == 1250.00
    assert "id" in json_data["data"]
    
    assert "_links" in json_data
    assert "self" in json_data["_links"]