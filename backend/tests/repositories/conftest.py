"""Repository test fixtures."""

from collections.abc import Callable
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Hotel, Project, Role, Room, RoomType, User


@pytest.fixture(autouse=True)
def create_schema(database_engine) -> None:
    Base.metadata.create_all(database_engine)


@pytest.fixture
def base_entities(database_session: Session) -> dict[str, object]:
    now = datetime(2026, 7, 21, 9, 0)
    user = User(
        username="engineer", password_hash="hash", display_name="Engineer",
        role=Role.ENGINEER, created_at=now, updated_at=now,
    )
    other_user = User(
        username="other", password_hash="hash", display_name="Other",
        role=Role.ENGINEER, created_at=now, updated_at=now,
    )
    hotel = Hotel(name="Hotel A", created_at=now, updated_at=now)
    other_hotel = Hotel(name="Hotel B", created_at=now, updated_at=now)
    project = Project(name="Project A", hotel=hotel, created_at=now, updated_at=now)
    other_project = Project(
        name="Project B", hotel=other_hotel, created_at=now, updated_at=now
    )
    room_type = RoomType(name="King", hotel=hotel, created_at=now, updated_at=now)
    other_room_type = RoomType(
        name="King", hotel=other_hotel, created_at=now, updated_at=now
    )
    room = Room(
        hotel=hotel, room_type=room_type, room_number="101",
        created_at=now, updated_at=now,
    )
    other_room = Room(
        hotel=other_hotel, room_type=other_room_type, room_number="101",
        created_at=now, updated_at=now,
    )
    database_session.add_all([user, other_user, project, other_project, room, other_room])
    database_session.flush()
    return {
        "user": user, "other_user": other_user,
        "hotel": hotel, "other_hotel": other_hotel,
        "project": project, "other_project": other_project,
        "room": room, "other_room": other_room, "now": now,
    }
