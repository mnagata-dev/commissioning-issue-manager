"""Tests for the application foundation."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.core.config import Settings
from app.core.exceptions import ValidationError
from app.main import app, create_app


def test_create_app_returns_fastapi() -> None:
    """The application factory returns FastAPI."""
    assert isinstance(create_app(), FastAPI)


def test_module_app_is_fastapi() -> None:
    """The module-level ASGI application is available."""
    assert isinstance(app, FastAPI)


def test_application_has_only_approved_routes() -> None:
    """Only approved API routes are registered."""
    paths = set(app.openapi()["paths"])
    assert "/" not in paths
    assert "/health" not in paths
    assert {path for path in paths if path.startswith("/api/")} == {
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/me",
        "/api/projects",
        "/api/projects/{project_id}/issues",
        "/api/issues/{issue_id}",
        "/api/issues/{issue_id}/comments",
        "/api/issues/{issue_id}/attachments",
        "/api/issues/{issue_id}/attachments/{attachment_id}",
        "/api/attachments/{attachment_id}",
        "/api/issues/{issue_id}/status",
    }


def test_attachment_routes_have_only_approved_methods_without_duplicates() -> None:
    paths = app.openapi()["paths"]

    assert set(paths["/api/issues/{issue_id}/attachments"]) == {"get", "post"}
    assert set(paths["/api/attachments/{attachment_id}"]) == {"get"}
    assert set(paths["/api/issues/{issue_id}/attachments/{attachment_id}"]) == {
        "delete"
    }


@pytest.mark.parametrize("session_secret", [None, ""])
def test_create_app_requires_session_secret(session_secret: str | None) -> None:
    with pytest.raises(RuntimeError, match="CIM_SESSION_SECRET"):
        create_app(Settings(session_secret=session_secret))


def test_application_error_uses_common_response() -> None:
    """Application errors use the designed safe response."""
    test_app = create_app()

    @test_app.get("/_test/error")
    def raise_validation_error() -> None:
        raise ValidationError()

    response = TestClient(test_app).get("/_test/error")
    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }


def test_request_validation_error_uses_common_safe_response() -> None:
    test_app = create_app()

    @test_app.get("/_test/validation")
    def require_integer(value: int) -> None:
        del value

    response = TestClient(test_app).get("/_test/validation", params={"value": "bad"})

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    assert "int_parsing" not in response.text
