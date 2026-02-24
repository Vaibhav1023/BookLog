"""
AuthService — registration and login business logic.

Returns (user, token) on success.
Raises descriptive exceptions on failure.
"""

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.jwt_utils import create_token


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, repository: UserRepository):
        self._repo = repository

    def register(self, email: str, password: str, name=None) -> tuple[User, str]:
        try:
            user = self._repo.create(email=email, password=password, name=name)
        except ValueError as e:
            raise AuthError(str(e))
        token = create_token(user.id, user.email)
        return user, token

    def login(self, email: str, password: str) -> tuple[User, str]:
        user = self._repo.verify_credentials(email, password)
        if user is None:
            raise AuthError("Invalid email or password.")
        token = create_token(user.id, user.email)
        return user, token
