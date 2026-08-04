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
    session.rollback.assert_called_once_with()


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


def test_list_comments_returns_dtos_in_repository_order(
    session, repositories, domain_entities
) -> None:
    issue_repository, user_repository, comment_repository = repositories
    first = domain_entities["comment"]
    second = MagicMock(
        id=8,
        comment="Resolved",
        creator=domain_entities["user"],
        created_at=first.created_at,
    )
    comment_repository.list_by_issue.return_value = [first, second]
    service = CommentService(session, issue_repository, user_repository, comment_repository)

    result = service.list_comments(6)

    assert [comment.id for comment in result] == [7, 8]
    assert result[0].comment == "Checked"
    assert result[0].created_by.id == 3
    assert result[0].created_by.display_name == "Engineer"
    issue_repository.find_by_id.assert_called_once_with(6)
    comment_repository.list_by_issue.assert_called_once_with(6)
    user_repository.find_by_id.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_list_comments_returns_empty_list(session, repositories) -> None:
    issue_repository, user_repository, comment_repository = repositories
    comment_repository.list_by_issue.return_value = []
    service = CommentService(session, issue_repository, user_repository, comment_repository)

    assert service.list_comments(6) == []
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_list_comments_issue_not_found_does_not_access_comments(
    session, repositories
) -> None:
    issue_repository, user_repository, comment_repository = repositories
    issue_repository.find_by_id.return_value = None
    service = CommentService(session, issue_repository, user_repository, comment_repository)

    with pytest.raises(NotFoundError):
        service.list_comments(99)

    comment_repository.list_by_issue.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
