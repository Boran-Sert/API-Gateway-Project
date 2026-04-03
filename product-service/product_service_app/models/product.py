from pydantic import BaseModel, Field
from uuid import uuid4



# --- Temel Ürün Verisi (Oluşturma/Güncelleme için) ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Ürün adı")
    price: float = Field(..., gt=0, description="Ürün fiyatı (0'dan büyük olmalı)")
    category: str = Field(
        ..., min_length=2, max_length=50, description="Ürün kategorisi"
    )
    stock: int = Field(..., ge=0, description="Stok adedi (0 veya daha fazla olmalı)")


# --- Yeni Ürün Oluşturma Modeli (API'ye POST ile gelen veri) ---
class ProductCreate(ProductBase):
    pass


# --- Veritabanı Modeli (ID içeren tam model) ---
# Domain katmanının modeli — veritabanı sorumluluğunu taşır (SRP).
class Product(ProductBase):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        alias="_id",
        description="Ürünün benzersiz ID'si (MongoDB'deki _id alanına karşılık gelir)",
    )

    model_config = {"populate_by_name": True}


# --- API Sunum Modeli (Resource Assembler Pattern) ---
# Domain modeline dokunmadan API temsili genişletilir (OCP).
# Bu bir Pydantic modeli değil, saf bir Assembler sınıfıdır.
class ProductResource:
    """Product domain modelinin API sunum katmanına dönüştürücüsü (SRP)."""

    @staticmethod
    def from_domain(product: "Product", base_path: str = "/api/products") -> dict:
        """
        Domain modelinden API resource sözlüğü üretir.
        Factory Method Pattern — dönüşüm mantığı tek yerde toplanır (SRP).
        """
        product_dict = product.model_dump(by_alias=False)
        product_dict["_links"] = {
            "self": {"href": f"{base_path}/{product.id}", "method": "GET"},
            "update": {"href": f"{base_path}/{product.id}", "method": "PUT"},
            "delete": {"href": f"{base_path}/{product.id}", "method": "DELETE"},
        }
        return product_dict


# --- API Yanıt Modelleri ---
class ProductResponse(BaseModel):
    message: str
    id: str