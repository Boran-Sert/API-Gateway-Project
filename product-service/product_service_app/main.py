from fastapi import FastAPI, Depends, Query
from product_service_app.services.product_service import ProductService

app = FastAPI()

@app.get("/products")
async def get_products(
    page: int = Query(1, ge=1), 
    limit: int = Query(5, ge=1), 
    service: ProductService = Depends()
):
    return await service.list_products(page, limit)