from user_service_app.models.user import User
from shared.base_repository import MongoRepository
from user_service_app.db import get_database

class UserRepository(MongoRepository[User]):
    """User veritabanı işlemleri için somut repository."""
    def __init__(self):
        # Veritabanı bağlantısını ve koleksiyonu al
        database = get_database()
        user_collection = database.get_collection("users")
        
        # Üst sınıfı (MongoRepository) doğru parametrelerle başlat
        super().__init__(collection=user_collection, model_class=User)