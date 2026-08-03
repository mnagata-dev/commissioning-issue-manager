"""Issue API integration tests."""

from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_current_user, get_issue_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.main import create_app
from app.schemas import CurrentUserResponse, IssueDetailResponse

CURRENT_USER = CurrentUserResponse(
    id=7, username="engineer@example.com", display_name="Engineer", role="ENGINEER"
)


@pytest.fixture
def issue_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(issue_service) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    application.dependency_overrides[get_issue_service] = lambda: issue_service
    with TestClient(application) as test_client:
        yield test_client


def detail_response() -> IssueDetailResponse:
    timestamp = datetime(2026, 8, 3, 10, 0)
    return IssueDetailResponse(
        id=101,
        project={"id": 2, "name": "Commissioning"},
        room=None,
        target_type="OTHER",
        target="Network",
        category="NETWORK",
        description="No communication.",
        status="OPEN",
        created_by={"id": 7, "display_name": "Engineer"},
        updated_by={"id": 7, "display_name": "Engineer"},
        created_at=timestamp,
        updated_at=timestamp,
        comments=[],
        attachments=[],
    )


def test_get_issue_detail_returns_service_response(client, issue_service) -> None:
    issue_service.get_issue_detail.return_value = detail_response()
    response = client.get("/api/issues/101")
    assert response.status_code == 200
    assert response.json()["project"] == {"id": 2, "name": "Commissioning"}
    assert response.json()["room"] is None
    assert response.json()["comments"] == []
    assert response.json()["attachments"] == []
    issue_service.get_issue_detail.assert_called_once_with(101)


def test_get_issue_detail_not_found(client, issue_service) -> None:
    issue_service.get_issue_detail.side_effect = NotFoundError("Issue not found.")
    assert client.get("/api/issues/999").status_code == 404


@pytest.mark.parametrize(
    ("method", "path", "payload", "service_method", "expected"),
    [
        (
            "put",
            "/api/issues/101",
            {"room_id": None, "target_type": "OTHER", "target": "Network", "category": "NETWORK", "description": "Updated"},
            "update_issue",
            {"id": 101, "message": "Issue updated"},
        ),
        (
            "patch",
            "/api/issues/101/status",
            {"status": "IN_PROGRESS"},
            "update_status",
            {"id": 101, "status": "IN_PROGRESS", "message": "Status updated"},
        ),
    ],
)
def test_write_routes_forward_authenticated_user(
    client, issue_service, method, path, payload, service_method, expected
) -> None:
    response = getattr(client, method)(path, json=payload)
    assert response.status_code == 200
    assert response.json() == expected
    service = getattr(issue_service, service_method)
    request = service.call_args.kwargs["request"]
    service.assert_called_once_with(issue_id=101, request=request, user_id=7)


@pytest.mark.parametrize(
    ("method", "path"),
    [("get", "/api/issues/101"), ("put", "/api/issues/101"), ("patch", "/api/issues/101/status")],
)
def test_issue_routes_require_authentication(method, path) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    with TestClient(application) as unauthenticated_client:
        response = getattr(unauthenticated_client, method)(path)
    assert response.status_code == 401
