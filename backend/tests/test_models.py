"""Database model mapping tests."""

from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (
    Attachment,
    Category,
    Comment,
    Hotel,
    Issue,
    Project,
    Role,
    Room,
    RoomType,
    Status,
    TargetType,
    User,
)


EXPECTED_TABLES = {
    "attachments", "comments", "hotels", "issues", "projects", "rooms",
    "room_types", "users",
}


def test_all_models_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_constraints_indexes_and_foreign_keys(database_engine) -> None:
    Base.metadata.create_all(database_engine)
    inspector = inspect(database_engine)

    assert {index["name"] for index in inspector.get_indexes("issues")} == {
        "ix_issues_category", "ix_issues_project_id", "ix_issues_room_id",
        "ix_issues_status", "ix_issues_target_type",
    }
    assert {constraint["name"] for constraint in inspector.get_unique_constraints("rooms")} == {
        "uq_rooms_hotel_id_room_number"
    }
    assert {foreign_key["name"] for foreign_key in inspector.get_foreign_keys("issues")} == {
        "fk_issues_created_by_users", "fk_issues_project_id_projects",
        "fk_issues_room_id_rooms", "fk_issues_updated_by_users",
    }
    check_names = {item["name"] for item in inspector.get_check_constraints("issues")}
    assert check_names == {
        "ck_issues_category", "ck_issues_status", "ck_issues_target_type"
    }


def test_enum_values_and_relationships(database_engine) -> None:
    Base.metadata.create_all(database_engine)
    now = datetime(2026, 7, 17, 0, 0)
    user = User(
        username="engineer", password_hash="hash", display_name="Engineer",
        role=Role.ENGINEER, created_at=now, updated_at=now,
    )
    hotel = Hotel(name="Hotel", created_at=now, updated_at=now)
    project = Project(name="Project", hotel=hotel, created_at=now, updated_at=now)
    room_type = RoomType(name="King", hotel=hotel, created_at=now, updated_at=now)
    room = Room(
        hotel=hotel, room_type=room_type, room_number="101",
        created_at=now, updated_at=now,
    )
    issue = Issue(
        project=project, room=room, target_type=TargetType.ROOM,
        category=Category.LIGHTING, description="Description", status=Status.OPEN,
        creator=user, updater=user, created_at=now, updated_at=now,
    )
    comment = Comment(issue=issue, comment="Comment", creator=user, created_at=now)
    attachment = Attachment(
        issue=issue, file_name="file.jpg", original_file_name="photo.jpg",
        file_path="issues/file.jpg", mime_type="image/jpeg", file_size=1,
        uploader=user, uploaded_at=now,
    )

    with Session(database_engine) as session:
        session.add_all([comment, attachment])
        session.commit()
        session.expire_all()
        stored = session.get(Issue, issue.id)
        assert stored is not None
        assert stored.target_type is TargetType.ROOM
        assert stored.category is Category.LIGHTING
        assert stored.status is Status.OPEN
        assert stored.project.hotel is hotel
        assert stored.comments[0].comment == "Comment"
        assert stored.attachments[0].file_size == 1


def test_undefined_enum_value_is_rejected(database_engine) -> None:
    Base.metadata.create_all(database_engine)
    now = datetime(2026, 7, 17, 0, 0)
    with Session(database_engine) as session:
        session.add(
            User(
                username="invalid", password_hash="hash", display_name="Invalid",
                role="UNDEFINED", created_at=now, updated_at=now,  # type: ignore[arg-type]
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
