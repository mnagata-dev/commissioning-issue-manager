"""Authentication API integration tests."""

from collections.abc import Generator

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_auth_service
from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.main import create_app
from app.schemas import CurrentUserResponse

TEST_USER = CurrentUserResponse(
    id=1,
    username="engineer1@example.com",
    display_name="Engineer 1",
    role="ENGINEER",
)


class StubAuthService:
    """Controllable authentication service for HTTP integration tests."""

    def login(self, username: str, password: str) -> CurrentUserResponse:
        if username != TEST_USER.username or password != "password":
            raise AuthenticationError()
        return TEST_USER

    def get_current_user(self, user_id: int) -> CurrentUserResponse:
        if user_id != TEST_USER.id:
            raise AuthenticationError()
        return TEST_USER


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_auth_service] = StubAuthService
    with TestClient(application) as test_client:
        yield test_client


def test_login_creates_session_cookie_and_returns_user(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "engineer1@example.com", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json() == {"user": TEST_USER.model_dump()}
    assert "password_hash" not in response.text

    set_cookie = response.headers["set-cookie"]
    assert set_cookie.startswith("cim_session=")
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()
    assert "path=/" in set_cookie.lower()
    assert "max-age=28800" in set_cookie.lower()
    assert "secure" not in set_cookie.lower()

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json() == TEST_USER.model_dump()


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("unknown@example.com", "password"),
        ("engineer1@example.com", "wrong-password"),
    ],
)
def test_login_failure_is_generic_and_does_not_create_session(
    client: TestClient,
    username: str,
    password: str,
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "AUTHENTICATION_ERROR",
            "message": "Authentication failed.",
        }
    }
    assert "cim_session" not in client.cookies


def test_login_request_validation_uses_common_bad_request_response(
    client: TestClient,
) -> None:
    response = client.post("/api/auth/login", json={})

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    assert "detail" not in response.json()
    assert "cim_session" not in client.cookies


def test_me_without_session_returns_unauthorized(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_logout_clears_session(client: TestClient) -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"username": "engineer1@example.com", "password": "password"},
    )
    assert login_response.status_code == 200

    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    assert client.get("/api/auth/me").status_code == 401


def test_logout_without_session_returns_unauthorized(client: TestClient) -> None:
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
