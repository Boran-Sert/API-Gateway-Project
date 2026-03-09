from app.database import db
import uuid

class ProductRepository:
    """Ürünler için veritabani işlemlerini yöneten OOP """
    
    def __init__(self):
        self.collection = db.get_collection("products")

    async def get_all_products(self) -> list:
        products = []
        cursor = self.collection.find({})
        async for document in cursor:
            document["id"] = document.pop("_id")
            products.append(document)
        return products

    async def create_product(self, product_data: dict) -> dict:
        product_data["_id"] = str(uuid.uuid4())
        await self.collection.insert_one(product_data)
        product_data["id"] = product_data.pop("_id")
        return product_data

    # SİLME FONKSİYONU
    async def delete_product(self, product_id: str) -> bool:
        result = await self.collection.delete_one({"_id": product_id})
        return result.deleted_count > 0