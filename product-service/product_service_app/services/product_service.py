from product_service_app.models.product import (
    Product,
    ProductCreate,
    ProductResponse,
    ProductResource,
)
from shared.hateoas import HateoasBuilder
from shared.exceptions import NotFoundException
from shared.base_repository import AbstractRepository


class ProductService:
    """Ürün iş mantığı servisi (SRP — sadece iş kurallarını yönetir)."""

    def __init__(self, repository: AbstractRepository[Product]):
        self._repository = repository
        self._hateoas_builder = HateoasBuilder(base_url="/api")

    async def get_all_paginated(self, page: int, limit: int):
        """Ürünleri sayfalı şekilde getirir — Resource Assembler + Strategy Pattern."""
        skip = (page - 1) * limit
        products = await self._repository.find_all(skip=skip, limit=limit)
        total_products = await self._repository.count()

        # Strategy Pattern: HateoasBuilder'a item_serializer olarak
        # ProductResource.from_domain factory method'u geçilir.
        # Bu sayede builder domain modeline bağımlı kalmaz (DIP).
        paginated_response = self._hateoas_builder.collection_response(
            items=products,
            resource_name="products",
            page=page,
            per_page=limit,
            total=total_products,
            item_serializer=ProductResource.from_domain,
        )

        return paginated_response

    async def get_product_by_id(self, product_id: str) -> dict:
        """ID ile tek bir ürün getirir — Resource Assembler Pattern."""
        product = await self._repository.find_by_id(product_id)
        if not product:
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        # Domain → Resource dönüşümü factory method ile yapılır (SRP)
        product_resource = ProductResource.from_domain(product)
        product_resource["_links"]["collection"] = {"href": "/api/products"}
        return product_resource

    async def update_product(
        self, product_id: str, product_data: ProductCreate
    ) -> dict:
        """Bir ürünü günceller ve HATEOAS linkleri ile döner."""
        if not await self._repository.find_by_id(product_id):
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        updated_product_model = Product(id=product_id, **product_data.model_dump())

        result = await self._repository.update(product_id, updated_product_model)
        final_product = result if result else updated_product_model

        return {
            "message": "Ürün başarıyla güncellendi",
            "id": final_product.id,
            "_links": {
                "self": {"href": f"/api/products/{final_product.id}"},
                "collection": {"href": "/api/products"},
            },
        }

    async def delete_product(self, product_id: str) -> dict:
        """Bir ürünü siler ve HATEOAS linkleri ile döner."""
        was_deleted = await self._repository.delete(product_id)
        if not was_deleted:
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        return {
            "message": "Ürün başarıyla silindi",
            "_links": {"collection": {"href": "/api/products"}},
        }

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Yeni bir ürünü MongoDB'ye kaydeder."""
        product_to_save = Product(**product_data.model_dump())
        created_product = await self._repository.create(product_to_save)
        return ProductResponse(message="Ürün başarıyla eklendi", id=created_product.id)
