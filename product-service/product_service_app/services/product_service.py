from product_service_app.repositories.product_repository import ProductRepository
from product_service_app.models.product import Product, ProductCreate, ProductResponse
from shared.hateoas import HateoasBuilder
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
        return self._hateoas_builder.collection_response(
            items=products,
            resource_name="products",
            page=page,
            per_page=limit,
            total=total_products,
        )
    
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
