"""Tests for the application foundation."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import ValidationError
from app.main import app, create_app


def test_create_app_returns_fastapi() -> None:
    """The application factory returns FastAPI."""
    assert isinstance(create_app(), FastAPI)


def test_module_app_is_fastapi() -> None:
    """The module-level ASGI application is available."""
    assert isinstance(app, FastAPI)


def test_application_has_no_undefined_routes() -> None:
    """No root, health, or business route is registered."""
    paths = {route.path for route in app.routes}
    assert "/" not in paths
    assert "/health" not in paths
    assert not any(path.startswith("/api/") for path in paths)


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
