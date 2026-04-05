from fastapi import FastAPI, Depends, Query, status
from dotenv import load_dotenv
load_dotenv()
from product_service_app.services.product_service import ProductService
from product_service_app.models.product import ProductCreate, ProductResponse
from product_service_app.db import lifespan
from product_service_app.repositories.product_repository import ProductRepository
from shared.exceptions import AppException, app_exception_handler
from shared.logging import setup_logging
from shared.security import RoleChecker
from shared.middleware import LoggingMiddleware
from shared.metrics import setup_metrics
app = FastAPI(
    title="Product Service", 
    version="1.0.0",
    lifespan=lifespan
)
logger = setup_logging("product-service")
app.add_exception_handler(AppException, app_exception_handler)
setup_metrics(app, "product-service")
app.add_middleware(LoggingMiddleware, logger=logger)
def get_product_repository():
    return ProductRepository()
def get_product_service(repo: ProductRepository = Depends(get_product_repository)):
    return ProductService(repository=repo)
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
@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    ID ile tek bir ürün getirir.
    """
    return await service.get_product_by_id(product_id)
@app.post(
    "/products", 
    status_code=status.HTTP_201_CREATED, 
    response_model=ProductResponse,
    dependencies=[Depends(RoleChecker(["admin"]))]
)
async def create_product(
    product: ProductCreate, 
    service: ProductService = Depends(get_product_service)
):
    """
    Yeni bir ürün oluşturur ve 201 Created döner.
    """
    return await service.create_product(product)
@app.put("/products/{product_id}",
         dependencies=[Depends(RoleChecker(["admin"]))])
async def update_product(
    product_id: str,
    product: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Mevcut bir ürünü günceller.
    """
    return await service.update_product(product_id, product)
@app.delete("/products/{product_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Bir ürünü siler.
    """
    return await service.delete_product(product_id)
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "product-service"}