"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.session import get_db_session
from app.models.enums import Role
from app.repositories import (
    AttachmentRepository,
    CommentRepository,
    IssueRepository,
    ProjectRepository,
    RoomRepository,
    UserRepository,
)
from app.schemas import CurrentUserResponse
from app.services import AuthService, IssueService, ProjectService

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_auth_service(session: DatabaseSession) -> AuthService:
    """Construct the authentication service for the current request."""
    return AuthService(UserRepository(session))


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def get_project_service(session: DatabaseSession) -> ProjectService:
    """Construct the project service for the current request."""
    return ProjectService(ProjectRepository(session))


ProjectServiceDependency = Annotated[ProjectService, Depends(get_project_service)]


def get_issue_service(session: DatabaseSession) -> IssueService:
    """Construct the issue service for the current request."""
    return IssueService(
        session,
        ProjectRepository(session),
        RoomRepository(session),
        IssueRepository(session),
        UserRepository(session),
        CommentRepository(session),
        AttachmentRepository(session),
    )


IssueServiceDependency = Annotated[IssueService, Depends(get_issue_service)]


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
    "get_issue_service",
    "get_project_service",
    "require_administrator",
]
