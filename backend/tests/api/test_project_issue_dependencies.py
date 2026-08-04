"""Project and Issue service dependency tests."""

from unittest.mock import MagicMock, patch

from app.api.deps import (
    get_ai_service,
    get_attachment_service,
    get_comment_service,
    get_issue_service,
    get_project_service,
)
from app.clients import OllamaClient
from app.repositories import (
    AttachmentRepository,
    CommentRepository,
    IssueRepository,
    ProjectRepository,
    RoomRepository,
    UserRepository,
)
from app.services import StorageService


def test_get_ai_service_constructs_required_dependencies() -> None:
    session = MagicMock()
    provider = MagicMock()

    with patch("app.clients.ollama_client.Client", return_value=provider):
        service = get_ai_service(session)

    assert isinstance(service.project_repository, ProjectRepository)
    assert isinstance(service.room_repository, RoomRepository)
    assert isinstance(service.ollama_client, OllamaClient)
    assert service.project_repository.session is session
    assert service.room_repository.session is session
    session.assert_not_called()
    provider.chat.assert_not_called()


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


def test_get_comment_service_constructs_required_repositories() -> None:
    session = MagicMock()

    service = get_comment_service(session)

    assert service.session is session
    assert isinstance(service.issue_repository, IssueRepository)
    assert isinstance(service.user_repository, UserRepository)
    assert isinstance(service.comment_repository, CommentRepository)
    assert all(
        repository.session is session
        for repository in (
            service.issue_repository,
            service.user_repository,
            service.comment_repository,
        )
    )
    session.assert_not_called()


def test_get_attachment_service_constructs_required_dependencies() -> None:
    session = MagicMock()

    service = get_attachment_service(session)

    assert service.session is session
    assert isinstance(service.issue_repository, IssueRepository)
    assert isinstance(service.user_repository, UserRepository)
    assert isinstance(service.attachment_repository, AttachmentRepository)
    assert isinstance(service.storage_service, StorageService)
    assert all(
        repository.session is session
        for repository in (
            service.issue_repository,
            service.user_repository,
            service.attachment_repository,
        )
    )
    session.assert_not_called()
