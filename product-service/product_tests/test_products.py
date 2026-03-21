from fastapi.testclient import TestClient
from product_service_app.main import app, get_repository
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

    async def update_product(self, product_id: str, update_data: dict):
        for p in self.fake_db:
            if p["id"] == product_id:
                p.update(update_data)
                return p
        return None

    async def get_paginated_products(self, page: int, limit: int):
        start = (page - 1) * limit
        end = start + limit
        return self.fake_db[start:end], len(self.fake_db)

mock_repo_instance = MockProductRepository()
app.dependency_overrides[get_repository] = lambda: mock_repo_instance

# --- TESTLER ---
def test_get_empty_products_list():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_create_product():
    new_product = {"name": "Klavye", "price": 100, "category": "Elektronik", "stock": 10}
    response = client.post("/products", json=new_product)
    assert response.status_code == 201
    assert "id" in response.json()["data"]

def test_delete_product():
    new_product = {"name": "Mouse", "price": 50, "category": "Elektronik", "stock": 5}
    create_res = client.post("/products", json=new_product)
    p_id = create_res.json()["data"]["id"]
    response = client.delete(f"/products/{p_id}")
    assert response.status_code == 200

def test_update_product():
    # 1. Önce ürün oluştur
    res = client.post("/products", json={"name": "Eski", "price": 10, "category": "X", "stock": 1})
    p_id = res.json()["data"]["id"]
    
    # 2. Güncelle
    up_data = {"name": "Yeni", "price": 20, "category": "X", "stock": 1}
    response = client.put(f"/products/{p_id}", json=up_data)
    
    # 3. Kontrol
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Yeni"