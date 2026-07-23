from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.models import (
    Attachment,
    Category,
    Comment,
    Hotel,
    Issue,
    Project,
    Role,
    Room,
    Status,
    TargetType,
    User,
)


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def domain_entities() -> dict[str, object]:
    timestamp = datetime(2026, 7, 23, 1, 0)
    hotel = Hotel(id=1, name="Hotel", created_at=timestamp, updated_at=timestamp)
    project = Project(
        id=2, hotel_id=hotel.id, name="Project", created_at=timestamp, updated_at=timestamp
    )
    project.hotel = hotel
    user = User(
        id=3,
        username="engineer",
        password_hash="hash",
        display_name="Engineer",
        role=Role.ENGINEER,
        created_at=timestamp,
        updated_at=timestamp,
    )
    room = Room(
        id=4,
        hotel_id=hotel.id,
        room_type_id=5,
        room_number="1203",
        display_name=None,
        created_at=timestamp,
        updated_at=timestamp,
    )
    issue = Issue(
        id=6,
        project=project,
        room=room,
        target_type=TargetType.ROOM,
        target=None,
        category=Category.LIGHTING,
        description="Description",
        status=Status.OPEN,
        creator=user,
        updater=user,
        created_at=timestamp,
        updated_at=timestamp,
    )
    comment = Comment(
        id=7, issue=issue, comment="Checked", creator=user, created_at=timestamp
    )
    attachment = Attachment(
        id=8,
        issue=issue,
        file_name="photo.jpg",
        original_file_name="photo.jpg",
        file_path="uploads/photo.jpg",
        mime_type="image/jpeg",
        file_size=100,
        uploader=user,
        uploaded_at=timestamp,
    )
    return {
        "hotel": hotel,
        "project": project,
        "user": user,
        "room": room,
        "issue": issue,
        "comment": comment,
        "attachment": attachment,
    }
