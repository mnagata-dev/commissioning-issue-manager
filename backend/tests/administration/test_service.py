"""AdministrationService business rules with mocked boundaries."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from app.models import Hotel, Project, Role, Room, RoomType, User
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
from app.services.administration_service import AdministrationService


@pytest.fixture
def mocked_service(monkeypatch) -> AdministrationService:
    monkeypatch.setattr(
        "app.services.administration_service.hash_password",
        lambda value: "hashed-password",
    )
    repositories = [MagicMock() for _ in range(5)]
    instance = AdministrationService(MagicMock(), MagicMock(), *repositories)
    instance.auth_service.login.return_value.role = "ADMINISTRATOR"
    instance.user_repository.find_by_username.return_value = None
    instance.room_repository.find_by_hotel_and_room_number.return_value = None
    instance.room_type_repository.find_by_id.return_value.hotel_id = 1
    for repository in repositories:
        repository.create.side_effect = lambda entity: (
            setattr(entity, "id", 9) or entity
        )
    return instance


CREATE_CASES = [
    ("hotel", CreateHotelRequest(name="H")),
    ("project", CreateProjectRequest(name="P", hotel_id=1)),
    ("room_type", CreateRoomTypeRequest(name="T", hotel_id=1)),
    ("room", CreateRoomRequest(hotel_id=1, room_type_id=2, room_number="101")),
    (
        "user",
        CreateUserRequest(
            username="new", display_name="N", role="ENGINEER", password="new-pass"
        ),
    ),
]


@pytest.mark.parametrize("target, command_input", CREATE_CASES)
def test_create_authentication_commit_and_safe_result(
    mocked_service, target, command_input
) -> None:
    with patch(
        "app.services.administration_service.begin_user_write_transaction"
    ) as begin:
        result = getattr(mocked_service, f"create_{target}")(
            "admin", "secret", command_input
        )
    mocked_service.auth_service.login.assert_called_once_with("admin", "secret")
    mocked_service.session.commit.assert_called_once()
    mocked_service.session.rollback.assert_not_called()
    assert result.model_dump() == {
        "target": target.replace("_", "-"),
        "id": 9,
        "operation": "create",
    }
    assert begin.call_count == int(target == "user")


@pytest.mark.parametrize("target, command_input", CREATE_CASES)
@pytest.mark.parametrize("failure", [AuthenticationError(), AuthorizationError()])
def test_authentication_and_authorization_rollback(
    mocked_service, target, command_input, failure
) -> None:
    if isinstance(failure, AuthenticationError):
        mocked_service.auth_service.login.side_effect = failure
    else:
        mocked_service.auth_service.login.return_value.role = "ENGINEER"
    with patch("app.services.administration_service.begin_user_write_transaction"):
        with pytest.raises(type(failure)):
            getattr(mocked_service, f"create_{target}")(
                "engineer", "secret", command_input
            )
    mocked_service.session.rollback.assert_called_once()
    mocked_service.session.commit.assert_not_called()
    getattr(mocked_service, f"{target}_repository").create.assert_not_called()


UPDATE_CASES = [
    ("hotel", Hotel, UpdateHotelRequest(name="Changed"), {"name": "Old"}),
    (
        "project",
        Project,
        UpdateProjectRequest(name="Changed"),
        {"name": "Old", "hotel_id": 1},
    ),
    (
        "room_type",
        RoomType,
        UpdateRoomTypeRequest(name="Changed"),
        {"name": "Old", "hotel_id": 1},
    ),
    (
        "room",
        Room,
        UpdateRoomRequest(display_name="Changed"),
        {"hotel_id": 1, "room_type_id": 2, "room_number": "101"},
    ),
    (
        "user",
        User,
        UpdateUserRequest(display_name="Changed"),
        {
            "username": "old",
            "display_name": "Old",
            "role": Role.ENGINEER,
            "password_hash": "old-hash",
        },
    ),
]


@pytest.mark.parametrize("target, model, command_input, values", UPDATE_CASES)
def test_update_and_omission(
    mocked_service, target, model, command_input, values
) -> None:
    timestamp = datetime(2026, 1, 1)
    entity = model(id=9, created_at=timestamp, updated_at=timestamp, **values)
    repository = getattr(mocked_service, f"{target}_repository")
    repository.find_by_id.return_value = entity
    with patch("app.services.administration_service.begin_user_write_transaction"):
        getattr(mocked_service, f"update_{target}")("admin", "secret", 9, command_input)
    assert entity.id == 9 and entity.created_at == timestamp
    assert entity.updated_at > timestamp and entity.updated_at.tzinfo is None
    for name, value in command_input.model_dump(exclude_unset=True).items():
        assert getattr(entity, name) == value
    if target in ("project", "room_type", "room"):
        assert entity.hotel_id == 1
    if target == "user":
        assert entity.role == Role.ENGINEER and entity.password_hash == "old-hash"
    repository.update.assert_called_once_with(entity)
    mocked_service.session.commit.assert_called_once()
    mocked_service.session.reset_mock()
    repository.update.reset_mock()
    updated_at = entity.updated_at
    with patch("app.services.administration_service.begin_user_write_transaction"):
        getattr(mocked_service, f"update_{target}")(
            "admin", "secret", 9, type(command_input)()
        )
    assert entity.updated_at == updated_at
    repository.update.assert_not_called()
    mocked_service.session.commit.assert_called_once()


@pytest.mark.parametrize("target, model, command_input, values", UPDATE_CASES)
def test_update_missing_and_engineer(
    mocked_service, target, model, command_input, values
) -> None:
    repository = getattr(mocked_service, f"{target}_repository")
    repository.find_by_id.return_value = None
    with patch("app.services.administration_service.begin_user_write_transaction"):
        with pytest.raises(NotFoundError):
            getattr(mocked_service, f"update_{target}")(
                "admin", "secret", 999, command_input
            )
    mocked_service.session.rollback.assert_called_once()
    mocked_service.session.reset_mock()
    mocked_service.auth_service.login.return_value.role = "ENGINEER"
    with patch("app.services.administration_service.begin_user_write_transaction"):
        with pytest.raises(AuthorizationError):
            getattr(mocked_service, f"update_{target}")(
                "engineer", "secret", 9, command_input
            )
    mocked_service.session.rollback.assert_called_once()
    repository.update.assert_not_called()


@pytest.mark.parametrize("count", [0, 1, 2])
def test_bootstrap_count_and_fixed_role(mocked_service, count) -> None:
    mocked_service.user_repository.count_all.return_value = count
    command_input = BootstrapAdminRequest(
        username="admin", display_name="Admin", password="pw"
    )
    with patch(
        "app.services.administration_service.begin_user_write_transaction"
    ) as begin:
        if count:
            with pytest.raises(BusinessRuleError):
                mocked_service.bootstrap_admin(command_input)
            mocked_service.session.rollback.assert_called_once()
            mocked_service.user_repository.create.assert_not_called()
        else:
            mocked_service.bootstrap_admin(command_input)
            user = mocked_service.user_repository.create.call_args.args[0]
            assert user.role == Role.ADMINISTRATOR
            mocked_service.session.commit.assert_called_once()
        begin.assert_called_once_with(mocked_service.session)
    mocked_service.auth_service.login.assert_not_called()


@pytest.mark.parametrize("count, allowed", [(1, False), (2, True)])
def test_administrator_guard_in_service(mocked_service, count, allowed) -> None:
    user = User(id=9, username="admin", role=Role.ADMINISTRATOR, display_name="Old")
    mocked_service.user_repository.find_by_id.return_value = user
    mocked_service.user_repository.count_by_role.return_value = count
    command_input = UpdateUserRequest(role="ENGINEER", display_name="Changed")
    with patch("app.services.administration_service.begin_user_write_transaction"):
        if allowed:
            mocked_service.update_user("admin", "pw", 9, command_input)
            assert user.role == Role.ENGINEER
        else:
            with pytest.raises(BusinessRuleError):
                mocked_service.update_user("admin", "pw", 9, command_input)
            assert user.role == Role.ADMINISTRATOR and user.display_name == "Old"
            mocked_service.session.rollback.assert_called_once()
            mocked_service.user_repository.update.assert_not_called()
