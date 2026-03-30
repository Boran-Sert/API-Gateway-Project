from product_service_app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self):
        self.repo = ProductRepository()

    async def list_products(self, page: int, limit: int):
        products, total = await self.repo.get_paginated_products(page, limit)
        
        # Richardson Level 3 (HATEOAS) Linkleri burada üretilir
        links = [{"rel": "self", "href": f"/api/products?page={page}&limit={limit}"}]
        if (page * limit) < total:
            links.append({"rel": "next", "href": f"/api/products?page={page+1}&limit={limit}"})
        
        return {"data": products, "total": total, "_links": links}