from fastapi import FastAPI, Depends, Query, status
from product_service_app.services.product_service import ProductService
from product_service_app.models.product import ProductCreate, ProductResponse
from product_service_app.db import lifespan
from shared.exceptions import AppException, app_exception_handler
from shared.metrics import setup_metrics

app = FastAPI(
    title="Product Service", 
    version="1.0.0",
    lifespan=lifespan
)

# Hata yakalama mekanizmasını ekle (örn: NotFoundException için 404 dönmek)
app.add_exception_handler(AppException, app_exception_handler)

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

# --- 2. GET: Tek Ürün Getirme ---
@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    ID ile tek bir ürün getirir.
    """
    return await service.get_product_by_id(product_id)

# --- 3. POST: Yeni Ürün Ekleme ---
@app.post(
    "/products", 
    status_code=status.HTTP_201_CREATED, 
    response_model=ProductResponse
)
async def create_product(
    product: ProductCreate, 
    service: ProductService = Depends(get_product_service)
):
    """
    Yeni bir ürün oluşturur ve 201 Created döner.
    """
    return await service.create_product(product)

# --- 4. PUT: Ürün Güncelleme ---
@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Mevcut bir ürünü günceller.
    """
    return await service.update_product(product_id, product)

# --- 5. DELETE: Ürün Silme ---
@app.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Bir ürünü siler.
    """
    return await service.delete_product(product_id)

# --- 6. HEALTH CHECK ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "product-service"}