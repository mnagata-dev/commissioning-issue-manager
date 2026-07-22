import pytest
from pydantic import ValidationError

from app.schemas import CurrentUserResponse, LoginRequest


def test_login_request_accepts_valid_input() -> None:
    request = LoginRequest(username="engineer@example.com", password="password")
    assert request.model_dump() == {
        "username": "engineer@example.com",
        "password": "password",
    }


@pytest.mark.parametrize("missing_field", ["username", "password"])
def test_login_request_requires_fields(missing_field: str) -> None:
    data = {"username": "engineer", "password": "password"}
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        LoginRequest.model_validate(data)


def test_login_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(username="engineer", password="password", token="x")


def test_current_user_response_accepts_valid_input() -> None:
    response = CurrentUserResponse(
        id=1, username="engineer", display_name="Engineer", role="ENGINEER"
    )
    assert response.role == "ENGINEER"
