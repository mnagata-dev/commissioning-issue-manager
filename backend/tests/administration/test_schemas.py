"""Administration input types, omission and existing constraints."""

import pytest
from pydantic import ValidationError

from app.schemas.administration import (
    BootstrapAdminRequest,
    CreateHotelRequest,
    CreateProjectRequest,
    CreateRoomRequest,
    CreateRoomTypeRequest,
    CreateUserRequest,
    UpdateHotelRequest,
    UpdateProjectRequest,
    UpdateRoomRequest,
    UpdateRoomTypeRequest,
    UpdateUserRequest,
)


@pytest.mark.parametrize(
    "schema",
    [
        CreateHotelRequest,
        CreateProjectRequest,
        CreateRoomTypeRequest,
        CreateRoomRequest,
        CreateUserRequest,
        BootstrapAdminRequest,
    ],
)
def test_create_required_fields(schema) -> None:
    with pytest.raises(ValidationError):
        schema()


@pytest.mark.parametrize(
    "schema, field",
    [
        (UpdateHotelRequest, "name"),
        (UpdateProjectRequest, "name"),
        (UpdateRoomTypeRequest, "name"),
        (UpdateRoomRequest, "room_type_id"),
        (UpdateRoomRequest, "room_number"),
        (UpdateUserRequest, "username"),
        (UpdateUserRequest, "display_name"),
        (UpdateUserRequest, "password"),
        (UpdateUserRequest, "role"),
    ],
)
def test_update_omission_and_explicit_null(schema, field) -> None:
    assert schema().model_dump(exclude_unset=True) == {}
    with pytest.raises(ValidationError):
        schema(**{field: None})


@pytest.mark.parametrize(
    "schema", [UpdateProjectRequest, UpdateRoomTypeRequest, UpdateRoomRequest]
)
def test_hotel_changes_rejected(schema) -> None:
    with pytest.raises(ValidationError):
        schema(hotel_id=2)


@pytest.mark.parametrize(
    "values",
    [
        {"hotel_id": "1", "name": "Project"},
        {"hotel_id": 1, "name": 42},
        {"hotel_id": True, "name": "Project"},
    ],
)
def test_strict_types(values) -> None:
    with pytest.raises(ValidationError):
        CreateProjectRequest(**values)


def test_room_nullable_display_and_no_extra_policies() -> None:
    assert UpdateRoomRequest(display_name=None).model_fields_set == {"display_name"}
    assert CreateHotelRequest(name="").name == ""
    user = CreateUserRequest(
        username="engineer@example.com",
        display_name="",
        password="",
        role="ENGINEER",
    )
    assert user.password == ""
    assert "password=" not in repr(user)
    with pytest.raises(ValidationError):
        UpdateUserRequest(role="MANAGER")
