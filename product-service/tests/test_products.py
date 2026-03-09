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

# KRİTİK DÜZELTME: Sınıfı bir kez oluşturup, FastAPI'nin hep bu aynı belleği kullanmasını sağlıyoruz
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
    # 1. Silmek için bir ürün oluştur
    new_product = {
        "name": "Silinecek Mouse",
        "price": 300.00,
        "category": "Elektronik",
        "stock": 15
    }
    create_response = client.post("/products", json=new_product)
    assert create_response.status_code == 201
    
    product_id = create_response.json()["data"]["id"]
    
    # 2. Ürünü sil
    delete_response = client.delete(f"/products/{product_id}")
    
    # 3. Başarı durumunu kontrol et
    assert delete_response.status_code == 200
    json_data = delete_response.json()
    assert json_data["success"] == True
    assert "_links" in json_data
    assert "collection" in json_data["_links"]
    assert json_data["_links"]["collection"]["href"] == "/products"