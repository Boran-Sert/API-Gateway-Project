from app.database import db
import uuid

class ProductRepository:
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

    async def delete_product(self, product_id: str) -> bool:
        result = await self.collection.delete_one({"_id": product_id})
        return result.deleted_count > 0

    # Güncelleme fonksiyonu
    async def update_product(self, product_id: str, update_data: dict) -> dict:
        result = await self.collection.find_one_and_update(
            {"_id": product_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = result.pop("_id")
        return result