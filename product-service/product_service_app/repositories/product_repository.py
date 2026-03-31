from product_service_app.database import db
import uuid

class ProductRepository:
    def __init__(self):
        self.collection = db.get_collection("products")

    async def get_paginated(self, page: int, limit: int):
        skip = (page - 1) * limit
        total_count = await self.collection.count_documents({})
        cursor = self.collection.find().skip(skip).limit(limit)
        products = []
        async for p in cursor:
            p["id"] = str(p.pop("_id"))
            products.append(p)
        return products, total_count