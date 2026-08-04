"""Comment API integration tests."""

from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_comment_service, get_current_user
from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.main import create_app
from app.schemas import CommentResponse, CurrentUserResponse

CURRENT_USER = CurrentUserResponse(
    id=7,
    username="engineer@example.com",
    display_name="Engineer",
    role="ENGINEER",
)


@pytest.fixture
def comment_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(comment_service) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    application.dependency_overrides[get_comment_service] = lambda: comment_service
    with TestClient(application) as test_client:
        yield test_client


def test_create_comment_returns_created_id(client, comment_service) -> None:
    comment_service.create_comment.return_value = 12

    response = client.post("/api/issues/6/comments", json={"comment": "Checked"})

    assert response.status_code == 200
    assert response.json() == {"id": 12, "message": "Comment created"}
    request = comment_service.create_comment.call_args.kwargs["request"]
    assert request.comment == "Checked"
    comment_service.create_comment.assert_called_once_with(
        issue_id=6,
        request=request,
        user_id=7,
    )


@pytest.mark.parametrize("payload", [{}, {"comment": ["invalid"]}, {"extra": True}])
def test_create_comment_rejects_invalid_request(client, comment_service, payload) -> None:
    response = client.post("/api/issues/6/comments", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    comment_service.create_comment.assert_not_called()


def test_create_comment_returns_service_validation_error(client, comment_service) -> None:
    comment_service.create_comment.side_effect = ValidationError(
        "Comment must not be empty."
    )

    response = client.post("/api/issues/6/comments", json={"comment": ""})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_comment_returns_issue_not_found(client, comment_service) -> None:
    comment_service.create_comment.side_effect = NotFoundError("Issue not found.")

    response = client.post("/api/issues/999/comments", json={"comment": "Checked"})

    assert response.status_code == 404


def test_list_comments_returns_items(client, comment_service) -> None:
    comment_service.list_comments.return_value = [
        CommentResponse(
            id=12,
            comment="Checked",
            created_by={"id": 7, "display_name": "Engineer"},
            created_at=datetime(2026, 8, 4, 10, 20),
        )
    ]

    response = client.get("/api/issues/6/comments")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 12,
                "comment": "Checked",
                "created_by": {"id": 7, "display_name": "Engineer"},
                "created_at": "2026-08-04T10:20:00",
            }
        ]
    }
    comment_service.list_comments.assert_called_once_with(6)


def test_list_comments_returns_empty_items(client, comment_service) -> None:
    comment_service.list_comments.return_value = []

    response = client.get("/api/issues/6/comments")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_list_comments_returns_issue_not_found(client, comment_service) -> None:
    comment_service.list_comments.side_effect = NotFoundError("Issue not found.")

    assert client.get("/api/issues/999/comments").status_code == 404


@pytest.mark.parametrize("method", ["get", "post"])
def test_comment_routes_require_authentication(method) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    with TestClient(application) as unauthenticated_client:
        response = getattr(unauthenticated_client, method)(
            "/api/issues/6/comments",
            **({"json": {"comment": "Checked"}} if method == "post" else {}),
        )

    assert response.status_code == 401
