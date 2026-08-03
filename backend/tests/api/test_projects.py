"""Project API integration tests."""

from collections.abc import Generator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_current_user, get_issue_service, get_project_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.main import create_app
from app.schemas import CurrentUserResponse, IssueListResponse, ProjectListResponse

CURRENT_USER = CurrentUserResponse(
    id=7,
    username="engineer@example.com",
    display_name="Engineer",
    role="ENGINEER",
)


@pytest.fixture
def services() -> dict[str, MagicMock]:
    return {"project": MagicMock(), "issue": MagicMock()}


@pytest.fixture
def client(services) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    application.dependency_overrides[get_project_service] = lambda: services["project"]
    application.dependency_overrides[get_issue_service] = lambda: services["issue"]
    with TestClient(application) as test_client:
        yield test_client


def test_list_projects_returns_exact_service_response(client, services) -> None:
    services["project"].list_projects.return_value = ProjectListResponse(
        projects=[{"id": 2, "name": "Commissioning", "hotel": {"id": 1, "name": "Hotel"}}]
    )

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert response.json() == {
        "projects": [{"id": 2, "name": "Commissioning", "hotel": {"id": 1, "name": "Hotel"}}]
    }
    services["project"].list_projects.assert_called_once_with(7)


def test_list_projects_returns_empty_list(client, services) -> None:
    services["project"].list_projects.return_value = ProjectListResponse(projects=[])
    assert client.get("/api/projects").json() == {"projects": []}


def test_list_issues_forwards_filters_and_pagination(client, services) -> None:
    services["issue"].list_issues.return_value = IssueListResponse(
        items=[], page=3, page_size=10, total=25
    )

    response = client.get(
        "/api/projects/2/issues",
        params={
            "status": "OPEN",
            "category": "LIGHTING",
            "target_type": "ROOM",
            "keyword": "lamp",
            "page": 3,
            "page_size": 10,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"items": [], "page": 3, "page_size": 10, "total": 25}
    services["issue"].list_issues.assert_called_once_with(
        2, "OPEN", "LIGHTING", "ROOM", "lamp", 3, 10
    )


def test_list_issues_uses_approved_defaults(client, services) -> None:
    services["issue"].list_issues.return_value = IssueListResponse(
        items=[], page=1, page_size=20, total=0
    )

    assert client.get("/api/projects/2/issues").status_code == 200
    services["issue"].list_issues.assert_called_once_with(
        2, None, None, None, None, 1, 20
    )


@pytest.mark.parametrize("parameter", ["page", "page_size"])
def test_list_issues_rejects_non_numeric_pagination(
    client, services, parameter
) -> None:
    response = client.get(
        "/api/projects/2/issues",
        params={parameter: "abc"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    assert "int_parsing" not in response.text
    services["issue"].list_issues.assert_not_called()


@pytest.mark.parametrize("error", [ValidationError(), NotFoundError("Project not found.")])
def test_list_issues_uses_common_application_error(client, services, error) -> None:
    services["issue"].list_issues.side_effect = error
    response = client.get("/api/projects/2/issues")
    assert response.status_code == error.status_code
    assert "error" in response.json()


def test_create_issue_forwards_authenticated_user(client, services) -> None:
    services["issue"].create_issue.return_value = 101
    payload = {
        "room_id": None,
        "target_type": "OTHER",
        "target": "Network",
        "category": "NETWORK",
        "description": "No communication.",
    }

    response = client.post("/api/projects/2/issues", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": 101, "message": "Issue created"}
    request = services["issue"].create_issue.call_args.kwargs["request"]
    services["issue"].create_issue.assert_called_once_with(
        project_id=2,
        request=request,
        user_id=7,
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "room_id": None,
            "target_type": "OTHER",
            "target": "Network",
            "category": "NETWORK",
            "description": ["not", "a", "string"],
        },
    ],
)
def test_create_issue_rejects_invalid_request_body(client, services, payload) -> None:
    response = client.post("/api/projects/2/issues", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    assert "detail" not in response.json()
    services["issue"].create_issue.assert_not_called()


@pytest.mark.parametrize("path", ["/api/projects", "/api/projects/2/issues"])
def test_project_routes_require_authentication(path) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    with TestClient(application) as unauthenticated_client:
        response = unauthenticated_client.get(path)
    assert response.status_code == 401
