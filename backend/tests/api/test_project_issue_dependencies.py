"""Project and Issue service dependency tests."""

from unittest.mock import MagicMock

from app.api.deps import get_issue_service, get_project_service
from app.repositories import (
    AttachmentRepository,
    CommentRepository,
    IssueRepository,
    ProjectRepository,
    RoomRepository,
    UserRepository,
)


def test_get_project_service_uses_request_session() -> None:
    session = MagicMock()

    service = get_project_service(session)

    assert isinstance(service.project_repository, ProjectRepository)
    assert service.project_repository.session is session
    session.assert_not_called()


def test_get_issue_service_constructs_required_repositories() -> None:
    session = MagicMock()

    service = get_issue_service(session)

    assert service.session is session
    assert isinstance(service.project_repository, ProjectRepository)
    assert isinstance(service.room_repository, RoomRepository)
    assert isinstance(service.issue_repository, IssueRepository)
    assert isinstance(service.user_repository, UserRepository)
    assert isinstance(service.comment_repository, CommentRepository)
    assert isinstance(service.attachment_repository, AttachmentRepository)
    assert all(
        repository.session is session
        for repository in (
            service.project_repository,
            service.room_repository,
            service.issue_repository,
            service.user_repository,
            service.comment_repository,
            service.attachment_repository,
        )
    )
    session.assert_not_called()
