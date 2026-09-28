"""Issue Edit API tests with real services, repositories and SQLite."""

from collections.abc import Generator
from datetime import datetime

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.models import Hotel, Project, Role, Room, RoomType, User
from app.schemas import CurrentUserResponse

ROOM_REQUEST = {
    "room_id": 1, "target_type": "ROOM", "target": None,
    "category": "LIGHTING", "description": "Original description",
}
OTHER_REQUEST = {
    "room_id": None, "target_type": "OTHER", "target": "Network",
    "category": "NETWORK", "description": "Updated description",
}


@pytest.fixture
def edit_client(database_engine: Engine) -> Generator[TestClient, None, None]:
    Base.metadata.create_all(database_engine)
    timestamp = datetime(2026, 9, 28)
    with Session(database_engine) as session:
        hotel = Hotel(id=1, name="Hotel", created_at=timestamp, updated_at=timestamp)
        project = Project(id=1, name="Project", hotel=hotel,
                          created_at=timestamp, updated_at=timestamp)
        room_type = RoomType(id=1, name="King", hotel=hotel,
                             created_at=timestamp, updated_at=timestamp)
        room = Room(id=1, room_number="1203", hotel=hotel, room_type=room_type,
                    created_at=timestamp, updated_at=timestamp)
        user = User(id=1, username="engineer", password_hash="unused",
                    display_name="Engineer", role=Role.ENGINEER,
                    created_at=timestamp, updated_at=timestamp)
        session.add_all([project, room, user])
        session.commit()

    def database() -> Generator[Session, None, None]:
        with Session(database_engine) as session:
            yield session

    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_db_session] = database
    application.dependency_overrides[get_current_user] = lambda: CurrentUserResponse(
        id=1, username="engineer", display_name="Engineer", role="ENGINEER"
    )
    with TestClient(application) as client:
        response = client.post("/api/projects/1/issues", json=ROOM_REQUEST)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        yield client


def test_update_switches_targets_and_preserves_status(edit_client: TestClient) -> None:
    for payload in (OTHER_REQUEST, ROOM_REQUEST):
        response = edit_client.put("/api/issues/1", json=payload)
        assert response.status_code == 200
        assert response.json() == {"id": 1, "message": "Issue updated"}
        detail = edit_client.get("/api/issues/1").json()
        for key in ("target_type", "target", "category", "description"):
            assert detail[key] == payload[key]
        assert (detail["room"]["id"] if detail["room"] else None) == payload["room_id"]
        assert detail["status"] == "OPEN"


@pytest.mark.parametrize("status", ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"])
def test_status_update_preserves_content(edit_client: TestClient, status: str) -> None:
    before = edit_client.get("/api/issues/1").json()
    response = edit_client.patch("/api/issues/1/status", json={"status": status})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "status": status, "message": "Status updated"}
    after = edit_client.get("/api/issues/1").json()
    assert after["status"] == status
    for key in ("room", "target_type", "target", "category", "description", "created_at"):
        assert after[key] == before[key]


@pytest.mark.parametrize("changes", [
    {"target_type": ""}, {"category": ""}, {"description": ""},
    {"room_id": None}, {"target": "Invalid for ROOM"},
    {"target_type": "OTHER", "room_id": None, "target": None},
    {"target_type": "OTHER", "room_id": None, "target": ""},
    {"status": "CLOSED"},
])
def test_invalid_update_does_not_save(edit_client: TestClient, changes: dict) -> None:
    before = edit_client.get("/api/issues/1").json()
    response = edit_client.put("/api/issues/1", json={**ROOM_REQUEST, **changes})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert edit_client.get("/api/issues/1").json() == before


@pytest.mark.parametrize("field", ["target_type", "category", "description"])
def test_missing_required_field_does_not_save(edit_client: TestClient, field: str) -> None:
    before = edit_client.get("/api/issues/1").json()
    payload = dict(ROOM_REQUEST)
    del payload[field]
    assert edit_client.put("/api/issues/1", json=payload).status_code == 400
    assert edit_client.get("/api/issues/1").json() == before


def test_invalid_status_does_not_save(edit_client: TestClient) -> None:
    before = edit_client.get("/api/issues/1").json()
    response = edit_client.patch("/api/issues/1/status", json={"status": "INVALID"})
    assert response.status_code == 400
    assert edit_client.get("/api/issues/1").json() == before


@pytest.mark.parametrize(("method", "suffix", "payload"), [
    ("GET", "", None), ("PUT", "", ROOM_REQUEST),
    ("PATCH", "/status", {"status": "CLOSED"}),
])
def test_missing_issue(
    edit_client: TestClient, method: str, suffix: str, payload: dict | None
) -> None:
    response = edit_client.request(method, f"/api/issues/999{suffix}", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND_ERROR"


@pytest.mark.parametrize(("method", "suffix", "payload"), [
    ("GET", "", None), ("PUT", "", OTHER_REQUEST),
    ("PATCH", "/status", {"status": "CLOSED"}),
])
def test_unauthenticated_edit_does_not_save(
    edit_client: TestClient, method: str, suffix: str, payload: dict | None
) -> None:
    before = edit_client.get("/api/issues/1").json()
    current_user = edit_client.app.dependency_overrides.pop(get_current_user)
    response = edit_client.request(method, f"/api/issues/1{suffix}", json=payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"
    edit_client.app.dependency_overrides[get_current_user] = current_user
    assert edit_client.get("/api/issues/1").json() == before
