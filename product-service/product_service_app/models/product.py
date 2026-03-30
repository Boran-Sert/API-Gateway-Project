from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    category: str
    stock: int = Field(ge=0)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str