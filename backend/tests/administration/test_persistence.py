"""Real SQLite repository writes, rollback, references and concurrency."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier
from unittest.mock import patch

import pytest
from conftest import make_service
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, BusinessRuleError, NotFoundError
from app.core.security import verify_password
from app.models import Hotel, Project, Role, Room, RoomType, User
from app.repositories import (
    HotelRepository,
    ProjectRepository,
    RoomRepository,
    RoomTypeRepository,
    UserRepository,
)
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

CASES = [
    (
        "hotel",
        Hotel,
        HotelRepository,
        CreateHotelRequest,
        UpdateHotelRequest,
        {"name": "H"},
        {"name": "New"},
    ),
    (
        "project",
        Project,
        ProjectRepository,
        CreateProjectRequest,
        UpdateProjectRequest,
        {"name": "P"},
        {"name": "New"},
    ),
    (
        "room_type",
        RoomType,
        RoomTypeRepository,
        CreateRoomTypeRequest,
        UpdateRoomTypeRequest,
        {"name": "T"},
        {"name": "New"},
    ),
    (
        "room",
        Room,
        RoomRepository,
        CreateRoomRequest,
        UpdateRoomRequest,
        {"room_number": "101"},
        {"display_name": "New"},
    ),
    (
        "user",
        User,
        UserRepository,
        CreateUserRequest,
        UpdateUserRequest,
        {
            "username": "engineer@example.com",
            "display_name": "E",
            "role": "ENGINEER",
            "password": "pw",
        },
        {"display_name": "New"},
    ),
]


def inputs(service, target, create_schema, values):
    values = values.copy()
    if target in ("project", "room_type", "room"):
        hotel = service.create_hotel(
            "admin", "admin-pass", CreateHotelRequest(name="Parent")
        )
        values["hotel_id"] = hotel.id
    if target == "room":
        room_type = service.create_room_type(
            "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=hotel.id, name="Twin")
        )
        values["room_type_id"] = room_type.id
    return create_schema(**values)


@pytest.mark.parametrize(
    "target, model, repository, create_schema, update_schema, values, changes", CASES
)
def test_create_update_persist_and_repository_rollback(
    service,
    admin_id,
    administration_engine,
    target,
    model,
    repository,
    create_schema,
    update_schema,
    values,
    changes,
) -> None:
    request = inputs(service, target, create_schema, values)
    result = getattr(service, f"create_{target}")("admin", "admin-pass", request)
    with Session(administration_engine) as check:
        entity = check.get(model, result.id)
        created_at = entity.created_at
        before = {
            column.name: getattr(entity, column.name)
            for column in model.__table__.columns
        }
        if target == "room":
            assert entity.display_name is None
        if target == "user":
            assert entity.username == "engineer@example.com"
            assert verify_password("pw", entity.password_hash)
            assert entity.password_hash != "pw"
    getattr(service, f"update_{target}")(
        "admin", "admin-pass", result.id, update_schema(**changes)
    )
    with Session(administration_engine) as check:
        entity = check.get(model, result.id)
        assert entity.created_at == created_at and entity.updated_at >= created_at
        for name, value in changes.items():
            assert getattr(entity, name) == value
        if hasattr(entity, "hotel_id"):
            assert entity.hotel_id == before["hotel_id"]
        if target == "user":
            assert entity.password_hash == before["password_hash"]
        original = getattr(entity, next(iter(changes)))
        setattr(entity, next(iter(changes)), "Rolled back")
        repository(check).update(entity)
        check.rollback()
    with Session(administration_engine) as check:
        entity = check.get(model, result.id)
        assert getattr(entity, next(iter(changes))) == original
        updated_at = entity.updated_at
    getattr(service, f"update_{target}")(
        "admin", "admin-pass", result.id, update_schema()
    )
    with Session(administration_engine) as check:
        assert check.get(model, result.id).updated_at == updated_at


@pytest.mark.parametrize(
    "target, model, repository, create_schema, update_schema, values, changes", CASES
)
@pytest.mark.parametrize("failure_at", ["flush", "commit"])
def test_failed_create_update_rollback(
    service,
    admin_id,
    administration_engine,
    target,
    model,
    repository,
    create_schema,
    update_schema,
    values,
    changes,
    failure_at,
) -> None:
    request = inputs(service, target, create_schema, values)
    with patch.object(
        service.session, failure_at, side_effect=RuntimeError("private DB detail")
    ):
        with pytest.raises(RuntimeError):
            getattr(service, f"create_{target}")("admin", "admin-pass", request)
    with Session(administration_engine) as check:
        count = len(list(check.scalars(select(model))))
        assert count == int(target == "user")
    result = getattr(service, f"create_{target}")("admin", "admin-pass", request)
    with Session(administration_engine) as check:
        entity = check.get(model, result.id)
        before = {
            column.name: getattr(entity, column.name)
            for column in model.__table__.columns
        }
    with patch.object(
        service.session, failure_at, side_effect=RuntimeError("private DB detail")
    ):
        with pytest.raises(RuntimeError):
            getattr(service, f"update_{target}")(
                "admin", "admin-pass", result.id, update_schema(**changes)
            )
    with Session(administration_engine) as check:
        entity = check.get(model, result.id)
        assert {
            column.name: getattr(entity, column.name)
            for column in model.__table__.columns
        } == before


def test_bootstrap_existing_engineer_and_counts(service, administration_engine) -> None:
    timestamp = datetime(2026, 1, 1)
    with Session(administration_engine) as session:
        users = UserRepository(session)
        assert users.count_all() == users.count_by_role(Role.ADMINISTRATOR) == 0
        users.create(
            User(
                username="only-engineer",
                display_name="E",
                password_hash="hash",
                role=Role.ENGINEER,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
        session.commit()
    with pytest.raises(BusinessRuleError):
        service.bootstrap_admin(
            BootstrapAdminRequest(username="admin", display_name="A", password="pw")
        )
    with Session(administration_engine) as session:
        users = UserRepository(session)
        assert users.count_all() == users.count_by_role(Role.ENGINEER) == 1
        assert users.count_by_role(Role.ADMINISTRATOR) == 0


def test_roles_password_changes_and_last_admin_rollback(
    service, admin_id, administration_engine
) -> None:
    with pytest.raises(BusinessRuleError):
        service.update_user(
            "admin",
            "admin-pass",
            admin_id,
            UpdateUserRequest(
                role="ENGINEER",
                username="renamed",
                display_name="Changed",
                password="new",
            ),
        )
    with Session(administration_engine) as check:
        admin = check.get(User, admin_id)
        assert admin.username == "admin" and admin.display_name == "Administrator"
        assert admin.role == Role.ADMINISTRATOR and verify_password(
            "admin-pass", admin.password_hash
        )
    service.update_user(
        "admin", "admin-pass", admin_id, UpdateUserRequest(role="ADMINISTRATOR")
    )
    second = service.create_user(
        "admin",
        "admin-pass",
        CreateUserRequest(
            username="second", display_name="Second", role="ENGINEER", password="pw"
        ),
    )
    service.update_user(
        "admin",
        "admin-pass",
        second.id,
        UpdateUserRequest(role="ADMINISTRATOR", password="changed"),
    )
    service.update_user(
        "admin", "admin-pass", admin_id, UpdateUserRequest(role="ENGINEER")
    )
    with Session(administration_engine) as check:
        users = UserRepository(check)
        assert users.count_by_role(Role.ADMINISTRATOR) == 1
        assert verify_password("changed", check.get(User, second.id).password_hash)
    with pytest.raises(AuthenticationError):
        service.create_hotel("second", "pw", CreateHotelRequest(name="H"))


def test_duplicates_names_numbers_and_usernames(service, admin_id) -> None:
    h1 = service.create_hotel("admin", "admin-pass", CreateHotelRequest(name="Same"))
    h2 = service.create_hotel("admin", "admin-pass", CreateHotelRequest(name="Same"))
    for _ in range(2):
        service.create_project(
            "admin", "admin-pass", CreateProjectRequest(name="Same", hotel_id=h1.id)
        )
        service.create_room_type(
            "admin", "admin-pass", CreateRoomTypeRequest(name="Same", hotel_id=h1.id)
        )
    t1 = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(name="T", hotel_id=h1.id)
    )
    t2 = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(name="T", hotel_id=h2.id)
    )
    r1 = service.create_room(
        "admin",
        "admin-pass",
        CreateRoomRequest(hotel_id=h1.id, room_type_id=t1.id, room_number="101"),
    )
    service.update_room(
        "admin", "admin-pass", r1.id, UpdateRoomRequest(room_number="101")
    )
    service.create_room(
        "admin",
        "admin-pass",
        CreateRoomRequest(hotel_id=h2.id, room_type_id=t2.id, room_number="101"),
    )
    r2 = service.create_room(
        "admin",
        "admin-pass",
        CreateRoomRequest(hotel_id=h1.id, room_type_id=t1.id, room_number="102"),
    )
    with pytest.raises(BusinessRuleError):
        service.create_room(
            "admin",
            "admin-pass",
            CreateRoomRequest(hotel_id=h1.id, room_type_id=t1.id, room_number="101"),
        )
    with pytest.raises(BusinessRuleError):
        service.update_room(
            "admin", "admin-pass", r2.id, UpdateRoomRequest(room_number="101")
        )
    with pytest.raises(BusinessRuleError):
        service.create_user(
            "admin",
            "admin-pass",
            CreateUserRequest(
                username="admin", display_name="A", role="ENGINEER", password="pw"
            ),
        )
    user = service.create_user(
        "admin",
        "admin-pass",
        CreateUserRequest(
            username="other", display_name="O", role="ENGINEER", password="pw"
        ),
    )
    with pytest.raises(BusinessRuleError):
        service.update_user(
            "admin", "admin-pass", user.id, UpdateUserRequest(username="admin")
        )
    service.update_user(
        "admin", "admin-pass", admin_id, UpdateUserRequest(username="admin")
    )


def test_references_and_room_type_changes(service, admin_id) -> None:
    with pytest.raises(NotFoundError):
        service.create_project(
            "admin", "admin-pass", CreateProjectRequest(hotel_id=999, name="P")
        )
    with pytest.raises(NotFoundError):
        service.create_room_type(
            "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=999, name="T")
        )
    h1 = service.create_hotel("admin", "admin-pass", CreateHotelRequest(name="H"))
    h2 = service.create_hotel("admin", "admin-pass", CreateHotelRequest(name="H"))
    t1 = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=h1.id, name="T")
    )
    t2 = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=h1.id, name="T")
    )
    t3 = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=h2.id, name="T")
    )
    with pytest.raises(NotFoundError):
        service.create_room(
            "admin",
            "admin-pass",
            CreateRoomRequest(hotel_id=999, room_type_id=t1.id, room_number="101"),
        )
    with pytest.raises(NotFoundError):
        service.create_room(
            "admin",
            "admin-pass",
            CreateRoomRequest(hotel_id=h1.id, room_type_id=999, room_number="101"),
        )
    with pytest.raises(BusinessRuleError):
        service.create_room(
            "admin",
            "admin-pass",
            CreateRoomRequest(hotel_id=h1.id, room_type_id=t3.id, room_number="101"),
        )
    room = service.create_room(
        "admin",
        "admin-pass",
        CreateRoomRequest(hotel_id=h1.id, room_type_id=t1.id, room_number="101"),
    )
    with pytest.raises(BusinessRuleError):
        service.update_room(
            "admin", "admin-pass", room.id, UpdateRoomRequest(room_type_id=t3.id)
        )
    with pytest.raises(NotFoundError):
        service.update_room(
            "admin", "admin-pass", room.id, UpdateRoomRequest(room_type_id=999)
        )
    service.update_room(
        "admin", "admin-pass", room.id, UpdateRoomRequest(room_type_id=t2.id)
    )


def test_room_type_lookup_and_create_rollback(administration_engine) -> None:
    with Session(administration_engine) as session:
        repository = RoomTypeRepository(session)
        assert repository.find_by_id(999) is None
        now = datetime(2026, 1, 1)
        hotel = HotelRepository(session).create(
            Hotel(name="H", created_at=now, updated_at=now)
        )
        room_type = repository.create(
            RoomType(hotel_id=hotel.id, name="T", created_at=now, updated_at=now)
        )
        assert repository.find_by_id(room_type.id) is room_type
        session.rollback()
    with Session(administration_engine) as check:
        assert list(check.scalars(select(Hotel))) == []
        assert list(check.scalars(select(RoomType))) == []


def test_foreign_key_failure(administration_engine) -> None:
    with Session(administration_engine) as session:
        now = datetime(2026, 1, 1)
        with pytest.raises(IntegrityError):
            RoomTypeRepository(session).create(
                RoomType(hotel_id=999, name="T", created_at=now, updated_at=now)
            )
        session.rollback()


def test_concurrent_bootstrap(service_factory, administration_engine) -> None:
    barrier = Barrier(2)

    def bootstrap(index):
        instance = service_factory()
        try:
            barrier.wait(timeout=5)
            instance.bootstrap_admin(
                BootstrapAdminRequest(
                    username=f"admin{index}", display_name="A", password="pw"
                )
            )
            return True
        except BusinessRuleError, OperationalError:
            return False
        finally:
            instance.session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(bootstrap, (1, 2))) == 1
    with Session(administration_engine) as check:
        assert UserRepository(check).count_by_role(Role.ADMINISTRATOR) == 1


def test_concurrent_demotion(
    service, admin_id, service_factory, administration_engine
) -> None:
    second = service.create_user(
        "admin",
        "admin-pass",
        CreateUserRequest(
            username="second",
            display_name="S",
            password="admin-pass",
            role="ADMINISTRATOR",
        ),
    )
    barrier = Barrier(2)

    def demote(user):
        instance = service_factory()
        try:
            barrier.wait(timeout=5)
            instance.update_user(
                user[0], "admin-pass", user[1], UpdateUserRequest(role="ENGINEER")
            )
            return True
        except BusinessRuleError, OperationalError:
            return False
        finally:
            instance.session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(demote, (("admin", admin_id), ("second", second.id)))) == 1
    with Session(administration_engine) as check:
        assert UserRepository(check).count_by_role(Role.ADMINISTRATOR) == 1


def test_write_lock_failure_rolls_back(
    service, admin_id, administration_engine
) -> None:
    engine = create_engine(administration_engine.url, connect_args={"timeout": 0})
    instance = make_service(Session(engine))
    try:
        with administration_engine.connect() as lock:
            lock.exec_driver_sql("BEGIN IMMEDIATE")
            with pytest.raises(OperationalError):
                instance.update_user(
                    "admin",
                    "admin-pass",
                    admin_id,
                    UpdateUserRequest(display_name="Changed"),
                )
            assert not instance.session.in_transaction()
            lock.rollback()
        with Session(administration_engine) as check:
            assert check.get(User, admin_id).display_name == "Administrator"
    finally:
        instance.session.close()
        engine.dispose()


@pytest.mark.parametrize(
    "target, model, repository, create_schema, update_schema, values, changes", CASES
)
def test_repository_create_rollback_for_all_targets(
    service,
    admin_id,
    administration_engine,
    target,
    model,
    repository,
    create_schema,
    update_schema,
    values,
    changes,
) -> None:
    command_input = inputs(service, target, create_schema, values)
    now = datetime(2026, 1, 1)
    data = command_input.model_dump()
    if target == "user":
        data["password_hash"] = data.pop("password")
    with Session(administration_engine) as session:
        entity = repository(session).create(
            model(**data, created_at=now, updated_at=now)
        )
        new_id = entity.id
        session.rollback()
    with Session(administration_engine) as check:
        assert check.get(model, new_id) is None


def test_update_username_to_unused_value_persists(
    service, admin_id, administration_engine
) -> None:
    user = service.create_user(
        "admin",
        "admin-pass",
        CreateUserRequest(
            username="engineer", display_name="Engineer", role="ENGINEER", password="pw"
        ),
    )
    service.update_user(
        "admin", "admin-pass", user.id, UpdateUserRequest(username="renamed-engineer")
    )
    with Session(administration_engine) as check:
        assert check.get(User, user.id).username == "renamed-engineer"


def test_update_room_number_to_unused_value_persists(
    service, admin_id, administration_engine
) -> None:
    request = inputs(service, "room", CreateRoomRequest, {"room_number": "101"})
    room = service.create_room("admin", "admin-pass", request)
    service.update_room(
        "admin", "admin-pass", room.id, UpdateRoomRequest(room_number="102")
    )
    with Session(administration_engine) as check:
        updated_room = check.get(Room, room.id)
        assert updated_room.room_number == "102"
        assert updated_room.hotel_id == request.hotel_id


@pytest.mark.parametrize("constraint", ["username", "room_number", "required", "role"])
def test_database_constraints_rollback(
    service, admin_id, administration_engine, constraint
) -> None:
    hotel = service.create_hotel("admin", "admin-pass", CreateHotelRequest(name="H"))
    room_type = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=hotel.id, name="T")
    )
    service.create_room(
        "admin",
        "admin-pass",
        CreateRoomRequest(
            hotel_id=hotel.id, room_type_id=room_type.id, room_number="101"
        ),
    )
    now = datetime(2026, 1, 1)
    with Session(administration_engine) as session:
        with pytest.raises(IntegrityError):
            if constraint == "username":
                UserRepository(session).create(
                    User(
                        username="admin",
                        display_name="A",
                        role=Role.ENGINEER,
                        password_hash="hash",
                        created_at=now,
                        updated_at=now,
                    )
                )
            elif constraint == "room_number":
                RoomRepository(session).create(
                    Room(
                        hotel_id=hotel.id,
                        room_type_id=room_type.id,
                        room_number="101",
                        created_at=now,
                        updated_at=now,
                    )
                )
            elif constraint == "required":
                HotelRepository(session).create(
                    Hotel(name=None, created_at=now, updated_at=now)
                )
            else:
                UserRepository(session).create(
                    User(
                        username="invalid",
                        display_name="I",
                        role="UNKNOWN",
                        password_hash="hash",
                        created_at=now,
                        updated_at=now,
                    )
                )
        session.rollback()
    with Session(administration_engine) as check:
        assert UserRepository(check).count_all() == 1
        assert len(list(check.scalars(select(Hotel)))) == 1
        assert len(list(check.scalars(select(Room)))) == 1
