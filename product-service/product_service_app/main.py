from fastapi import FastAPI, Depends, Query, status
from product_service_app.services.product_service import ProductService
from product_service_app.models.product import ProductCreate, ProductResponse
from product_service_app.db import lifespan
from shared.metrics import setup_metrics

app = FastAPI(
    title="Product Service", 
    version="1.0.0",
    lifespan=lifespan
)

# Prometheus metriklerini ayarla
setup_metrics(app, "product-service")

# Dependency Injection
def get_product_service():
    return ProductService()

# --- 1. GET: Ürün Listeleme ---
@app.get("/products", include_in_schema=True)
async def get_products(
    page: int = Query(1, ge=1), 
    limit: int = Query(5, ge=1, le=100),
    service: ProductService = Depends(get_product_service)
):
    """
    Tüm ürünleri sayfalama ve HATEOAS desteği ile döner.
    """
    return await service.get_all_paginated(page, limit)

# --- 2. POST: Yeni Ürün Ekleme ---
@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate, 
    service: ProductService = Depends(get_product_service)
):
    """
    Yeni bir ürün oluşturur ve 201 Created döner.
    """
    return await service.create_product(product)

# --- 3. HEALTH CHECK ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "product-service"}