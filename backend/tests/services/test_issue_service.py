from copy import copy
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Category, Status, TargetType
from app.schemas import CreateIssueRequest, UpdateIssueRequest, UpdateIssueStatusRequest
from app.services import IssueService


@pytest.fixture
def repositories(domain_entities):
    repositories = {name: MagicMock() for name in (
        "project", "room", "issue", "user", "comment", "attachment"
    )}
    repositories["project"].find_by_id.return_value = domain_entities["project"]
    repositories["room"].find_by_id.return_value = domain_entities["room"]
    repositories["issue"].find_by_id.return_value = domain_entities["issue"]
    repositories["user"].find_by_id.return_value = domain_entities["user"]
    repositories["comment"].list_by_issue.return_value = [domain_entities["comment"]]
    repositories["attachment"].list_by_issue.return_value = [domain_entities["attachment"]]
    return repositories


@pytest.fixture
def service(session, repositories) -> IssueService:
    return IssueService(
        session,
        repositories["project"],
        repositories["room"],
        repositories["issue"],
        repositories["user"],
        repositories["comment"],
        repositories["attachment"],
    )


def room_request(**changes) -> CreateIssueRequest:
    data = {
        "room_id": 4,
        "target_type": "ROOM",
        "target": None,
        "category": "LIGHTING",
        "description": "Description",
    }
    data.update(changes)
    return CreateIssueRequest(**data)


def update_request(**changes) -> UpdateIssueRequest:
    data = room_request().model_dump()
    data.update(changes)
    return UpdateIssueRequest(**data)


def test_list_issues_returns_summaries_with_offset_and_unchanged_filters(
    service, repositories, domain_entities, session
) -> None:
    repositories["issue"].list_by_project.return_value = [domain_entities["issue"]]

    result = service.list_issues(2, "OPEN", "LIGHTING", "ROOM", "lamp", 3, 20)

    assert [item.id for item in result] == [6]
    repositories["issue"].list_by_project.assert_called_once_with(
        2, "OPEN", "LIGHTING", "ROOM", "lamp", 40, 20
    )
    repositories["issue"].count_by_project.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.parametrize(("page", "page_size"), [(0, 1), (1, 0)])
def test_list_issues_rejects_non_positive_pagination(
    service, repositories, page, page_size
) -> None:
    with pytest.raises(ValidationError):
        service.list_issues(2, None, None, None, None, page, page_size)
    repositories["issue"].list_by_project.assert_not_called()


@pytest.mark.parametrize(
    ("status", "category", "target_type"),
    [("BAD", None, None), (None, "BAD", None), (None, None, "BAD")],
)
def test_list_issues_rejects_invalid_filters(
    service, repositories, status, category, target_type
) -> None:
    with pytest.raises(ValidationError):
        service.list_issues(2, status, category, target_type, None, 1, 20)
    repositories["issue"].list_by_project.assert_not_called()


def test_list_issues_project_not_found(service, repositories) -> None:
    repositories["project"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.list_issues(99, None, None, None, None, 1, 20)


def test_get_issue_detail_includes_repository_order(
    service, repositories, domain_entities, session
) -> None:
    result = service.get_issue_detail(6)
    assert result.id == 6
    assert [comment.id for comment in result.comments] == [7]
    assert [attachment.id for attachment in result.attachments] == [8]
    repositories["comment"].list_by_issue.assert_called_once_with(6)
    repositories["attachment"].list_by_issue.assert_called_once_with(6)
    session.commit.assert_not_called()


def test_get_issue_detail_not_found(service, repositories) -> None:
    repositories["issue"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.get_issue_detail(99)


@pytest.mark.parametrize(
    "issue_request",
    [room_request(), room_request(room_id=None, target_type="OTHER", target="Network")],
)
def test_create_issue_success_sets_open_and_commits(
    service, repositories, session, issue_request
) -> None:
    repositories["issue"].create.side_effect = lambda issue: setattr(issue, "id", 10) or issue

    result = service.create_issue(2, issue_request, 3)

    assert result == 10
    created = repositories["issue"].create.call_args.args[0]
    assert created.status is Status.OPEN
    assert created.target_type is TargetType(issue_request.target_type)
    assert created.category is Category(issue_request.category)
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


@pytest.mark.parametrize(
    "issue_request",
    [
        room_request(target_type="BAD"),
        room_request(room_id=None),
        room_request(target="target"),
        room_request(target_type="OTHER", target="Network"),
        room_request(room_id=None, target_type="OTHER", target=None),
        room_request(category="BAD"),
        room_request(description=""),
    ],
)
def test_create_issue_validation_failure_rolls_back_without_create(
    service, repositories, session, issue_request
) -> None:
    with pytest.raises(ValidationError):
        service.create_issue(2, issue_request, 3)
    repositories["issue"].create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once_with()


def test_create_issue_missing_resources(service, repositories, session) -> None:
    repositories["user"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.create_issue(2, room_request(), 99)
    session.rollback.assert_called_once_with()


def test_create_issue_project_not_found(service, repositories) -> None:
    repositories["project"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.create_issue(99, room_request(), 3)


def test_create_issue_room_not_found(service, repositories) -> None:
    repositories["room"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.create_issue(2, room_request(), 3)


def test_create_issue_room_hotel_mismatch(service, repositories, domain_entities) -> None:
    domain_entities["room"].hotel_id = 99
    with pytest.raises(ValidationError):
        service.create_issue(2, room_request(), 3)


def test_create_issue_repository_failure_rolls_back(service, repositories, session) -> None:
    repositories["issue"].create.side_effect = RuntimeError("database")
    with pytest.raises(RuntimeError):
        service.create_issue(2, room_request(), 3)
    session.rollback.assert_called_once_with()
    session.commit.assert_not_called()


def test_update_issue_updates_all_editable_fields(
    service, repositories, domain_entities, session
) -> None:
    issue = domain_entities["issue"]
    request = update_request(
        room_id=None,
        target_type="OTHER",
        target="Network",
        category="NETWORK",
        description="Updated",
    )

    service.update_issue(6, request, 3)

    assert issue.room is None
    assert issue.target_type is TargetType.OTHER
    assert issue.target == "Network"
    assert issue.category is Category.NETWORK
    assert issue.description == "Updated"
    assert issue.updater is domain_entities["user"]
    repositories["issue"].update.assert_called_once_with(issue)
    session.commit.assert_called_once_with()


@pytest.mark.parametrize(
    "issue_request",
    [
        update_request(room_id=None),
        update_request(target="bad"),
        update_request(room_id=4, target_type="OTHER", target="Network"),
        update_request(room_id=None, target_type="OTHER", target=None),
        update_request(category="BAD"),
        update_request(description=""),
    ],
)
def test_update_issue_validation_failure(
    service, repositories, session, issue_request
) -> None:
    with pytest.raises(ValidationError):
        service.update_issue(6, issue_request, 3)
    repositories["issue"].update.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once_with()


def test_update_issue_missing_issue_or_user(service, repositories) -> None:
    repositories["issue"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.update_issue(99, update_request(), 3)


def test_update_issue_user_not_found(service, repositories) -> None:
    repositories["user"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.update_issue(6, update_request(), 99)


def test_update_issue_room_hotel_mismatch(service, domain_entities) -> None:
    domain_entities["room"].hotel_id = 99
    with pytest.raises(ValidationError):
        service.update_issue(6, update_request(), 3)


def test_update_issue_repository_failure_rolls_back(service, repositories, session) -> None:
    repositories["issue"].update.side_effect = RuntimeError("database")
    with pytest.raises(RuntimeError):
        service.update_issue(6, update_request(), 3)
    session.rollback.assert_called_once_with()


def test_update_status_changes_only_status_updater_and_timestamp(
    service, repositories, domain_entities, session
) -> None:
    issue = domain_entities["issue"]
    original = copy(issue)
    service.update_status(6, UpdateIssueStatusRequest(status="CLOSED"), 3)
    assert issue.status is Status.CLOSED
    assert issue.description == original.description
    assert issue.category == original.category
    assert issue.target_type == original.target_type
    repositories["issue"].update.assert_called_once_with(issue)
    session.commit.assert_called_once_with()


def test_update_status_invalid(service, repositories, session) -> None:
    with pytest.raises(ValidationError):
        service.update_status(6, UpdateIssueStatusRequest(status="BAD"), 3)
    repositories["issue"].update.assert_not_called()
    session.rollback.assert_called_once_with()


def test_update_status_missing_issue_or_user(service, repositories) -> None:
    repositories["user"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.update_status(6, UpdateIssueStatusRequest(status="OPEN"), 99)


def test_update_status_issue_not_found(service, repositories) -> None:
    repositories["issue"].find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.update_status(99, UpdateIssueStatusRequest(status="OPEN"), 3)


def test_update_status_repository_failure_rolls_back(service, repositories, session) -> None:
    repositories["issue"].update.side_effect = RuntimeError("database")
    with pytest.raises(RuntimeError):
        service.update_status(6, UpdateIssueStatusRequest(status="OPEN"), 3)
    session.rollback.assert_called_once_with()
