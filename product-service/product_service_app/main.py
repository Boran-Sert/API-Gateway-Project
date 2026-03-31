from fastapi import FastAPI, Depends, Query
from product_service_app.services.product_service import ProductService

app = FastAPI(title="Product Service", version="1.0.0")

# Dependency Injection (Servis katmanını enjekte ediyoruz)
def get_product_service():
    return ProductService()

@app.get("/products")
async def get_products(
    page: int = Query(1, ge=1), 
    limit: int = Query(5, ge=1, le=100),
    service: ProductService = Depends(get_product_service)
):
    """
    Tüm ürünleri sayfalama ve HATEOAS desteği ile döner.
    """
    return await service.get_all_paginated(page, limit)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "product-service"}