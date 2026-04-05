from user_service_app.models.user import User, UserUpdate
from shared.base_repository import AbstractRepository
class UserService:
    def __init__(self, repository: AbstractRepository[User]):
        self._repository = repository
    async def get_or_create_profile(self, user_id: str, user_email: str) -> User:
        """
        Kullanıcı profilini ID ile arar. Bulamazsa, e-posta ve varsayılan
        kullanıcı adıyla yeni bir profil oluşturur.
        """
        user = await self._repository.find_by_id(user_id)
        if not user:
            default_username = user_email.split('@')[0]
            new_user_profile = User(id=user_id, email=user_email, username=default_username)
            user = await self._repository.create(new_user_profile)
        return user
    async def get_my_profile(self, user_id: str, user_email: str) -> dict:
        """Mevcut kullanıcının profilini getirir ve HATEOAS linkleri ekler."""
        user = await self.get_or_create_profile(user_id, user_email)
        user_dict = user.model_dump()
        user_dict["_links"] = {
            "self": {"href": "/users/me"},
            "update": {"href": "/users/me", "method": "PUT"},
        }
        return user_dict
    async def update_my_profile(self, user_id: str, user_email: str, user_data: UserUpdate) -> dict:
        """Mevcut kullanıcının profilini günceller."""
        existing_user = await self.get_or_create_profile(user_id, user_email)
        update_data = user_data.model_dump(exclude_unset=True)
        updated_user = existing_user.model_copy(update=update_data)
        await self._repository.update(user_id, updated_user)
        return {
            "message": "Profil başarıyla güncellendi",
            "id": updated_user.id,
            "_links": {"self": {"href": "/users/me"}},
        }