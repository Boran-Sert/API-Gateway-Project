from app.database import db
import uuid

class ProductRepository:
    def __init__(self):
        self.collection = db.get_collection("products")

    async def get_all_products(self) -> list:
        products = []
        cursor = self.collection.find({})
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            products.append(document)
        return products

    async def create_product(self, product_data: dict) -> dict:
        # Eğer manuel UUID kullanıyorsan kalsın, yoksa MongoDB kendi atar
        product_data["_id"] = str(uuid.uuid4())
        await self.collection.insert_one(product_data)
        product_data["id"] = product_data.pop("_id")
        return product_data

    async def delete_product(self, product_id: str) -> bool:
        result = await self.collection.delete_one({"_id": product_id})
        return result.deleted_count > 0

    async def update_product(self, product_id: str, update_data: dict) -> dict:
        result = await self.collection.find_one_and_update(
            {"_id": product_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = str(result.pop("_id"))
        return result
    
    # Sayfalama Fonksiyonu (Sınıfın İçine Dahil Edildi)
    async def get_paginated_products(self, page: int, limit: int):
        skip = (page - 1) * limit
        total_count = await self.collection.count_documents({})
        
        cursor = self.collection.find().skip(skip).limit(limit)
        products = []
        async for product in cursor:
            product["id"] = str(product.pop("_id"))
            products.append(product)
            
        return products, total_count