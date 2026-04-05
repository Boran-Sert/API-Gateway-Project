from product_service_app.models.product import Product
from shared.base_repository import MongoRepository
from product_service_app.db import get_database
class ProductRepository(MongoRepository[Product]):
    """Product veritabanı işlemleri için somut repository."""
    def __init__(self):
        database = get_database()
        product_collection = database.get_collection("products")
        super().__init__(collection=product_collection, model_class=Product)