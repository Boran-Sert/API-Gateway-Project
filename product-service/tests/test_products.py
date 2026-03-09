from fastapi.testclient import TestClient
from app.main import app, get_repository
import uuid

client = TestClient(app)

# --- SAHTE (MOCK) REPOSITORY ---
class MockProductRepository:
    def __init__(self):
        self.fake_db = []

    async def get_all_products(self):
        return self.fake_db

    async def create_product(self, product_data: dict):
        product_data["id"] = str(uuid.uuid4())
        self.fake_db.append(product_data)
        return product_data
        
    async def delete_product(self, product_id: str):
        initial_length = len(self.fake_db)
        self.fake_db = [p for p in self.fake_db if p.get("id") != product_id]
        return len(self.fake_db) < initial_length

mock_repo_instance = MockProductRepository()
app.dependency_overrides[get_repository] = lambda: mock_repo_instance

# --- TESTLER ---
def test_get_empty_products_list():
    response = client.get("/products")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 0
    assert json_data["_links"]["self"]["href"] == "/products"

def test_create_product():
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
    assert "id" in json_data["data"]
    assert "_links" in json_data
    assert "self" in json_data["_links"]

def test_delete_product():
    new_product = {
        "name": "Silinecek Mouse",
        "price": 300.00,
        "category": "Elektronik",
        "stock": 15
    }
    create_response = client.post("/products", json=new_product)
    product_id = create_response.json()["data"]["id"]
    
    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 200
    json_data = delete_response.json()
    assert json_data["success"] == True

# --- YENİ EKLENEN GÜNCELLEME TESTİ (RED AŞAMASI) ---
def test_update_product():
    """
    Ürün güncelleme testi (PUT /products/{id}).
    Fiyat ve stok gibi bilgilerin güncellenip güncellenmediği test edilir.
    """
    # 1. Önce güncellenecek bir ürün oluştur
    original_product = {
        "name": "Eski Kulaklık",
        "price": 500.00,
        "category": "Elektronik",
        "stock": 20
    }
    create_response = client.post("/products", json=original_product)
    product_id = create_response.json()["data"]["id"]
    
    # 2. Ürünün verilerini değiştir (Fiyata zam geldi, stok düştü)
    updated_product = {
        "name": "Yeni Nesil Kulaklık",
        "price": 750.00,
        "category": "Elektronik",
        "stock": 10
    }
    
    # 3. Henüz yazmadığımız PUT endpoint'ine istek at
    update_response = client.put(f"/products/{product_id}", json=updated_product)
    
    # 4. Beklenen durum 200 OK ve dönen verinin yeni verilerle eşleşmesi
    assert update_response.status_code == 200
    
    json_data = update_response.json()
    assert json_data["data"]["name"] == "Yeni Nesil Kulaklık"
    assert json_data["data"]["price"] == 750.00
    
    # RMM Seviye 3 HATEOAS kontrolü
    assert "_links" in json_data
    assert "self" in json_data["_links"]
    assert json_data["_links"]["self"]["href"] == f"/products/{product_id}"