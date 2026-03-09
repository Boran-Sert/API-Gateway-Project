from fastapi import FastAPI, status, Depends, HTTPException
from pydantic import BaseModel
from app.repository import ProductRepository

app = FastAPI(title="Product Service", version="1.0.0")

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    stock: int

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

# SİLME ENDPOINT'İ
@app.delete("/products/{product_id}")
async def delete_product(product_id: str, repo: ProductRepository = Depends(get_repository)):
    is_deleted = await repo.delete_product(product_id)
    if not is_deleted:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    return {
        "success": True,
        "message": "Ürün başarıyla silindi",
        "_links": {
            "collection": {"href": "/products", "method": "GET"}
        }
    }

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductCreate, repo: ProductRepository = Depends(get_repository)):
    updated_product = await repo.update_product(product_id, product.model_dump())
    if not updated_product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    return {
        "data": updated_product,
        "_links": {
            "self": {"href": f"/products/{product_id}", "method": "GET"},
            "collection": {"href": "/products", "method": "GET"}
        }
    }