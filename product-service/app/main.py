from fastapi import FastAPI, status
from pydantic import BaseModel
import uuid

app = FastAPI(title="Product Service", version="1.0.0")

# --- Modeller (Java'daki Class / DTO yapısı) ---
class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    stock: int

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    category: str
    stock: int

# Bir sonraki aşamada MongoDB'ye geçecek
fake_db = []

# --- Endpoint'ler ---
@app.get("/products")
async def get_products():
    """Tüm ürünleri listeler (RMM Seviye 3 HATEOAS uyumlu)."""
    return {
        "data": fake_db,
        "_links": {
            "self": {"href": "/products", "method": "GET"}
        }
    }

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """Yeni bir ürün ekler (RMM Seviye 3 HATEOAS uyumlu)"""
    # Yeni ürüne benzersiz bir ID ata
    new_product = ProductResponse(
        id=str(uuid.uuid4()),
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock
    )
    fake_db.append(new_product.model_dump())
    
    # RMM Seviye 3 HATEOAS formatında yanıt dön
    return {
        "data": new_product.model_dump(),
        "_links": {
            "self": {"href": f"/products/{new_product.id}", "method": "GET"},
            "collection": {"href": "/products", "method": "GET"}
        }
    }