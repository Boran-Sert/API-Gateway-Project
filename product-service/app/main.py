from fastapi import FastAPI, status, Depends
from pydantic import BaseModel
from app.repository import ProductRepository

app = FastAPI(title="Product Service", version="1.0.0")

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    stock: int

# Dependency Injection (Repository sınıfımızı enjekte ediyoruz)
def get_repository():
    return ProductRepository()

@app.get("/products")
async def get_products(repo: ProductRepository = Depends(get_repository)):
    products = await repo.get_all_products()
    return {
        "data": products,
        "_links": {"self": {"href": "/products", "method": "GET"}}
    }

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, repo: ProductRepository = Depends(get_repository)):
    new_product = await repo.create_product(product.model_dump())
    return {
        "data": new_product,
        "_links": {
            "self": {"href": f"/products/{new_product['id']}", "method": "GET"},
            "collection": {"href": "/products", "method": "GET"}
        }
    }