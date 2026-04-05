from fastapi.testclient import TestClient
from product_service_app.main import app, get_product_service
from product_service_app.services.product_service import ProductService
from unittest.mock import AsyncMock
client = TestClient(app)
class MockProductRepository:
    def __init__(self):
        self.fake_db = []
    async def get_all_products(self):
        return self.fake_db
    async def create(self, product_data):
        self.fake_db.append(product_data)
        return product_data
    async def delete(self, product_id: str):
        initial_length = len(self.fake_db)
        self.fake_db = [p for p in self.fake_db if p.get("_id") != product_id]                              
        return len(self.fake_db) < initial_length
    async def update(self, product_id: str, update_data):
        for p in self.fake_db:
            if p.get("_id") == product_id:
                p.update(update_data)
                return p
        return None
    async def get_all_paginated(self, page: int, limit: int):                                                                                          
        pass
def _override_service(mock_service):
    app.dependency_overrides[get_product_service] = lambda: mock_service
def test_get_empty_products_list():
    mock_service = AsyncMock(spec=ProductService)
    mock_service.get_all_paginated.return_value = {"data": [], "page": 1, "limit": 5, "total": 0}
    _override_service(mock_service)
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
def test_create_product():
    mock_service = AsyncMock(spec=ProductService)
    mock_service.create_product.return_value = {"message": "Success", "id": "1", "data": {"id": "1", "name": "Klavye"}}
    _override_service(mock_service)
    new_product = {"name": "Klavye", "price": 100, "category": "Elektronik", "stock": 10}
    response = client.post("/products", json=new_product, headers={"X-User-Role": "admin"})
    assert response.status_code == 201
    assert "id" in response.json()
def test_delete_product():
    mock_service = AsyncMock(spec=ProductService)
    mock_service.delete_product.return_value = {"message": "Ürün silindi"}
    _override_service(mock_service)
    response = client.delete("/products/1", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
def test_update_product():
    mock_service = AsyncMock(spec=ProductService)
    mock_service.update_product.return_value = {"message": "Success", "id": "1", "data": {"id": "1", "name": "Yeni"}}
    _override_service(mock_service)
    up_data = {"name": "Yeni", "price": 20, "category": "Elektronik", "stock": 1}
    response = client.put("/products/1", json=up_data, headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Yeni"