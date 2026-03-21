from shared.base_repository import MongoRepository
from user_service_app.models.user import User

class UserRepository(MongoRepository[User]):
    """
    MongoDB için User koleksiyonu işlemleri.
    MongoRepository'den miras aldığı için get_all, get_by_id gibi temel metodlar hazır gelir.
    """
    pass
