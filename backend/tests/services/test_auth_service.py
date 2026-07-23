from copy import copy
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AuthenticationError
from app.models import Role, User
from app.services import AuthService


@pytest.fixture
def user() -> User:
    timestamp = datetime(2026, 7, 23, 6, 0)
    return User(
        id=1,
        username="engineer@example.com",
        password_hash="stored-hash",
        display_name="Engineer",
        role=Role.ENGINEER,
        created_at=timestamp,
        updated_at=timestamp,
    )


@pytest.fixture
def repository(user: User) -> MagicMock:
    repository = MagicMock()
    repository.find_by_username.return_value = user
    repository.find_by_id.return_value = user
    return repository


def test_login_returns_current_user_for_email_username(
    repository: MagicMock, user: User
) -> None:
    original = copy(user)
    with patch("app.services.auth_service.verify_password", return_value=True) as verify:
        response = AuthService(repository).login(user.username, "submitted-password")

    repository.find_by_username.assert_called_once_with("engineer@example.com")
    verify.assert_called_once_with("submitted-password", "stored-hash")
    assert response.model_dump() == {
        "id": 1,
        "username": "engineer@example.com",
        "display_name": "Engineer",
        "role": "ENGINEER",
    }
    assert "password_hash" not in response.model_dump()
    assert user.username == original.username
    assert user.password_hash == original.password_hash
    assert user.display_name == original.display_name
    assert user.role == original.role


def test_login_passes_username_unchanged(repository: MagicMock) -> None:
    with patch("app.services.auth_service.verify_password", return_value=True):
        AuthService(repository).login("  Engineer  ", "password")
    repository.find_by_username.assert_called_once_with("  Engineer  ")


def test_login_unknown_username_raises_authentication_error(
    repository: MagicMock,
) -> None:
    repository.find_by_username.return_value = None
    with pytest.raises(AuthenticationError) as error:
        AuthService(repository).login("unknown", "password")
    assert error.value.message == "Authentication failed."


def test_login_wrong_password_uses_same_public_error(
    repository: MagicMock,
) -> None:
    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthenticationError) as error:
            AuthService(repository).login("engineer@example.com", "wrong")
    assert error.value.message == "Authentication failed."


def test_login_malformed_hash_uses_generic_authentication_error(
    repository: MagicMock,
) -> None:
    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            AuthService(repository).login("engineer@example.com", "password")


def test_get_current_user_returns_response(repository: MagicMock) -> None:
    response = AuthService(repository).get_current_user(1)
    repository.find_by_id.assert_called_once_with(1)
    assert response.id == 1
    assert response.role == "ENGINEER"


def test_get_current_user_missing_user_raises_authentication_error(
    repository: MagicMock,
) -> None:
    repository.find_by_id.return_value = None
    with pytest.raises(AuthenticationError, match="Authentication failed"):
        AuthService(repository).get_current_user(99)
