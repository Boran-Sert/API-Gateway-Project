from product_service_app.repositories.product_repository import ProductRepository
from product_service_app.models.product import Product, ProductCreate, ProductResponse
from shared.hateoas import HateoasBuilder
from shared.exceptions import NotFoundException
from shared.base_repository import AbstractRepository


class ProductService:
    def __init__(self):
        # Repository ismini '_repository' olarak sabitliyoruz
        self._repository: AbstractRepository[Product] = ProductRepository()
        self._hateoas_builder = HateoasBuilder(base_url="/products")

    async def get_all_paginated(self, page: int, limit: int):
        """Ürünleri AbstractRepository ve HateoasBuilder kullanarak sayfalı şekilde getirir."""
        skip = (page - 1) * limit
        products = await self._repository.find_all(skip=skip, limit=limit)
        total_products = await self._repository.count()
 
        # Yanıtı standart HATEOAS formatında oluştur
        paginated_response = self._hateoas_builder.collection_response(
            items=products,
            resource_name="products",
            page=page,
            per_page=limit,
            total=total_products,
        )

        # Her bir ürüne özel 'update' ve 'delete' linklerini ekle
        if "products" in paginated_response:
            for item in paginated_response["products"]:
                item_id = item.get("id")
                if item_id:
                    item["_links"] = {
                        "self": {"href": f"/products/{item_id}"},
                        "update": {"href": f"/products/{item_id}", "method": "PUT"},
                        "delete": {"href": f"/products/{item_id}", "method": "DELETE"},
                    }
        
        return paginated_response

    async def get_product_by_id(self, product_id: str) -> dict:
        """ID ile tek bir ürün getirir ve HATEOAS linkleri ekler."""
        product = await self._repository.find_by_id(product_id)
        if not product:
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        product_dict = product.model_dump()
        product_dict["_links"] = {
            "self": {"href": f"/products/{product.id}"},
            "update": {"href": f"/products/{product.id}", "method": "PUT"},
            "delete": {"href": f"/products/{product.id}", "method": "DELETE"},
            "collection": {"href": "/products"},
        }
        return product_dict

    async def update_product(self, product_id: str, product_data: ProductCreate) -> dict:
        """Bir ürünü günceller ve HATEOAS linkleri ile döner."""
        if not await self._repository.find_by_id(product_id):
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        updated_product_model = Product(id=product_id, **product_data.model_dump())
        
        # Eğer repo'dan None dönerse (değişiklik yoksa), orijinal modeli kullan
        result = await self._repository.update(product_id, updated_product_model)
        final_product = result if result else updated_product_model

        return {
            "message": "Ürün başarıyla güncellendi",
            "id": final_product.id,
            "_links": {
                "self": {"href": f"/products/{final_product.id}"},
                "collection": {"href": "/products"},
            },
        }

    async def delete_product(self, product_id: str) -> dict:
        """Bir ürünü siler ve HATEOAS linkleri ile döner."""
        was_deleted = await self._repository.delete(product_id)
        if not was_deleted:
            raise NotFoundException(resource_name="Product", resource_id=product_id)
        
        return {"message": "Ürün başarıyla silindi", "_links": {"collection": {"href": "/products"}}}

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Yeni bir ürünü MongoDB'ye kaydeder."""
        # AbstractRepository<T> arayüzü, Pydantic modelinin tamamını bekler.
        # ID alanı artık model içinde 'default_factory' ile otomatik olarak
        # oluşturulduğu için, burada sadece gelen veriyi modele aktarıyoruz.
        product_to_save = Product(**product_data.model_dump())

        # Depo (repository) üzerinden veritabanına kaydet
        created_product = await self._repository.create(product_to_save)

        # Standart yanıt modelini kullanarak istemciye cevap dön
        return ProductResponse(
            message="Ürün başarıyla eklendi", id=created_product.id
        )
