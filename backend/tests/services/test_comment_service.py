from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.schemas import CreateCommentRequest
from app.services import CommentService


@pytest.fixture
def repositories(domain_entities):
    issue_repository = MagicMock()
    user_repository = MagicMock()
    comment_repository = MagicMock()
    issue_repository.find_by_id.return_value = domain_entities["issue"]
    user_repository.find_by_id.return_value = domain_entities["user"]
    return issue_repository, user_repository, comment_repository


def test_create_comment_returns_id_and_commits(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    comment_repository.create.side_effect = (
        lambda comment: setattr(comment, "id", 12) or comment
    )
    service = CommentService(session, issue_repository, user_repository, comment_repository)

    result = service.create_comment(6, CreateCommentRequest(comment="Checked"), 3)

    assert result == 12
    created = comment_repository.create.call_args.args[0]
    assert created.comment == "Checked"
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_create_comment_issue_not_found(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    issue_repository.find_by_id.return_value = None
    service = CommentService(session, issue_repository, user_repository, comment_repository)
    with pytest.raises(NotFoundError):
        service.create_comment(99, CreateCommentRequest(comment="Checked"), 3)
    session.rollback.assert_called_once_with()


def test_create_comment_user_not_found(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    user_repository.find_by_id.return_value = None
    service = CommentService(session, issue_repository, user_repository, comment_repository)
    with pytest.raises(NotFoundError):
        service.create_comment(6, CreateCommentRequest(comment="Checked"), 99)


def test_create_comment_empty_rolls_back_without_create(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    service = CommentService(session, issue_repository, user_repository, comment_repository)
    with pytest.raises(ValidationError):
        service.create_comment(6, CreateCommentRequest(comment=""), 3)
    comment_repository.create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once_with()


def test_create_comment_repository_failure_rolls_back(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    comment_repository.create.side_effect = RuntimeError("database")
    service = CommentService(session, issue_repository, user_repository, comment_repository)
    with pytest.raises(RuntimeError):
        service.create_comment(6, CreateCommentRequest(comment="Checked"), 3)
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()
