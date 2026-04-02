from pydantic import BaseModel, Field
from uuid import uuid4

# --- Temel Ürün Verisi (Oluşturma/Güncelleme için) ---
# Bu model, bir ürünün temel alanlarını tanımlar.
class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Ürün adı")
    price: float = Field(..., gt=0, description="Ürün fiyatı (0'dan büyük olmalı)")
    category: str = Field(..., min_length=2, max_length=50, description="Ürün kategorisi")
    stock: int = Field(..., ge=0, description="Stok adedi (0 veya daha fazla olmalı)")


# --- Yeni Ürün Oluşturma Modeli (API'ye POST ile gelen veri) ---
# İstemci bu modeli kullanarak yeni bir ürün oluşturur. ID içermez.
class ProductCreate(ProductBase):
    pass


# --- Veritabanı Modeli (ID içeren tam model) ---
# BU SINIFIN EKSİKLİĞİ 'ImportError' HATASINA NEDEN OLUYORDU.
# Bu model, veritabanında saklanan veya tam olarak temsil edilen bir ürünü tanımlar.
# ProductCreate'den kalıtım alır ve bir 'id' alanı ekler.
class Product(ProductBase):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        alias="_id",
        description="Ürünün benzersiz ID'si (MongoDB'deki _id alanına karşılık gelir)"
    )


# --- API Yanıt Modelleri ---
# POST isteği sonrası istemciye dönülecek standart yanıt.
class ProductResponse(BaseModel):
    message: str
    id: str