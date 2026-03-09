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

# FastAPI'ye gerçek veritabanı yerine sahtesini kullanmasını söylüyoruz
app.dependency_overrides[get_repository] = lambda: MockProductRepository()

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