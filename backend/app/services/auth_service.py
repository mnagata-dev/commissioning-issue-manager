"""Authentication application service."""

from app.core.exceptions import AuthenticationError
from app.core.security import verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas import CurrentUserResponse


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def login(self, username: str, password: str) -> CurrentUserResponse:
        user = self.user_repository.find_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError()
        return self._to_response(user)

    def get_current_user(self, user_id: int) -> CurrentUserResponse:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise AuthenticationError()
        return self._to_response(user)

    @staticmethod
    def _to_response(user: User) -> CurrentUserResponse:
        return CurrentUserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=user.role.value,
        )
