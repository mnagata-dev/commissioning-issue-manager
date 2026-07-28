"""Authentication and role dependency tests."""

from unittest.mock import Mock

import pytest
from starlette.requests import Request

from app.api.deps import get_current_user, require_administrator
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.schemas import CurrentUserResponse


def _request_with_session(session: dict[str, object]) -> Request:
    return Request({"type": "http", "session": session})


def test_get_current_user_passes_session_user_id_to_service() -> None:
    expected = CurrentUserResponse(
        id=7,
        username="admin@example.com",
        display_name="Administrator",
        role="ADMINISTRATOR",
    )
    auth_service = Mock()
    auth_service.get_current_user.return_value = expected

    actual = get_current_user(_request_with_session({"user_id": 7}), auth_service)

    assert actual is expected
    auth_service.get_current_user.assert_called_once_with(7)


def test_get_current_user_rejects_missing_user_id() -> None:
    auth_service = Mock()

    with pytest.raises(AuthenticationError):
        get_current_user(_request_with_session({}), auth_service)

    auth_service.get_current_user.assert_not_called()


def test_get_current_user_propagates_invalid_user_authentication_error() -> None:
    auth_service = Mock()
    auth_service.get_current_user.side_effect = AuthenticationError()

    with pytest.raises(AuthenticationError):
        get_current_user(_request_with_session({"user_id": 999}), auth_service)


def test_require_administrator_returns_same_user() -> None:
    user = CurrentUserResponse(
        id=1,
        username="admin@example.com",
        display_name="Administrator",
        role="ADMINISTRATOR",
    )
    assert require_administrator(user) is user


def test_require_administrator_rejects_engineer() -> None:
    user = CurrentUserResponse(
        id=2,
        username="engineer@example.com",
        display_name="Engineer",
        role="ENGINEER",
    )
    with pytest.raises(AuthorizationError):
        require_administrator(user)
