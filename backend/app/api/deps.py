"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.session import get_db_session
from app.models.enums import Role
from app.repositories import UserRepository
from app.schemas import CurrentUserResponse
from app.services.auth_service import AuthService

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_auth_service(session: DatabaseSession) -> AuthService:
    """Construct the authentication service for the current request."""
    return AuthService(UserRepository(session))


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    request: Request,
    auth_service: AuthServiceDependency,
) -> CurrentUserResponse:
    """Resolve the authenticated user from the HTTP session."""
    user_id = request.session.get("user_id")
    if user_id is None:
        raise AuthenticationError()
    return auth_service.get_current_user(user_id)


CurrentUserDependency = Annotated[CurrentUserResponse, Depends(get_current_user)]


def require_administrator(
    user: CurrentUserDependency,
) -> CurrentUserResponse:
    """Require the authenticated user to have the Administrator role."""
    if user.role != Role.ADMINISTRATOR.value:
        raise AuthorizationError()
    return user


__all__ = [
    "get_auth_service",
    "get_current_user",
    "get_db_session",
    "require_administrator",
]
