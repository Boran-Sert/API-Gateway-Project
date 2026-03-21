from fastapi import FastAPI, status, Depends, Query
from pydantic import BaseModel
from product_service_app.repository import ProductRepository
from shared.exceptions import NotFoundException, AppException, app_exception_handler


app = FastAPI(title="Product Service", version="1.0.0")
app.add_exception_handler(AppException, app_exception_handler)

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    stock: int

def get_repository():
    return ProductRepository()


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
        raise NotFoundException("Product", product_id)
    
    return {
        "success": True,
        "message": "Ürün başarıyla silindi",
        "_links": {
            "collection": {"href": "/products", "method": "GET"}
        }
    }


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

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductCreate, repo: ProductRepository = Depends(get_repository)):
    updated = await repo.update_product(product_id, product.model_dump())
    if not updated:
        raise NotFoundException("Product", product_id)
    
    return {
        "data": updated,
        "_links": {
            "self": {"href": f"/products/{product_id}", "method": "GET"},
            "collection": {"href": "/products", "method": "GET"}
        }
    }