from fastapi import FastAPI, status, Depends, HTTPException, Query
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



# ... (Mevcut sınıflar ve get_repository aynı kalıyor)

@app.get("/products")
async def get_products(
    page: int = Query(1, ge=1), # Sayfa numarası, en az 1
    limit: int = Query(5, ge=1, le=100), # Sayfa başı ürün, max 100
    repo: ProductRepository = Depends(get_repository)
):
    # Veritabanından limitli ve atlamalı (skip) veriyi çek
    products, total_count = await repo.get_paginated_products(page, limit)
    
    # HATEOAS Linklerini Oluştur
    links = {
        "self": {"href": f"/products?page={page}&limit={limit}", "method": "GET"}
    }
    
    # Eğer sonraki sayfa varsa link ekle
    if (page * limit) < total_count:
        links["next"] = {"href": f"/products?page={page+1}&limit={limit}", "method": "GET"}
    
    # Eğer önceki sayfa varsa link ekle
    if page > 1:
        links["prev"] = {"href": f"/products?page={page-1}&limit={limit}", "method": "GET"}

    return {
        "data": products,
        "pagination": {
            "total": total_count,
            "page": page,
            "limit": limit
        },
        "_links": links
    }