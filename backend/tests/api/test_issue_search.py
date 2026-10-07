"""Issue search integration tests through the real service and SQLite."""

from collections.abc import Generator
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import Settings
from app.db.base import Base
from app.main import create_app
from app.models import Hotel, Issue, Project, Room, RoomType, User
from app.schemas import CurrentUserResponse


@pytest.fixture
def search_client(database_engine: Engine) -> Generator[TestClient, None, None]:
    """Seed contrasting issues and override only authentication and DB access."""
    Base.metadata.create_all(database_engine)
    timestamp = datetime(2026, 10, 7, 9, 0)
    with database_engine.begin() as connection:
        connection.execute(User.__table__.insert(), {
            "id": 1, "username": "engineer", "password_hash": "unused",
            "display_name": "Engineer", "role": "ENGINEER",
            "created_at": timestamp, "updated_at": timestamp,
        })
        connection.execute(Hotel.__table__.insert(), {
            "id": 1, "name": "Hotel",
            "created_at": timestamp, "updated_at": timestamp,
        })
        connection.execute(Project.__table__.insert(), [
            {
                "id": project_id, "hotel_id": 1, "name": f"Project {project_id}",
                "created_at": timestamp, "updated_at": timestamp,
            }
            for project_id in (1, 2)
        ])
        connection.execute(RoomType.__table__.insert(), {
            "id": 1, "hotel_id": 1, "name": "Standard",
            "created_at": timestamp, "updated_at": timestamp,
        })
        connection.execute(Room.__table__.insert(), {
            "id": 1, "hotel_id": 1, "room_type_id": 1, "room_number": "101",
            "created_at": timestamp, "updated_at": timestamp,
        })
        issues = []
        for issue_id in range(1, 8):
            issues.append({
                "id": issue_id,
                "project_id": 2 if issue_id == 7 else 1,
                "room_id": None if issue_id == 5 else 1,
                "target_type": "OTHER" if issue_id == 5 else "ROOM",
                "target": "Lobby" if issue_id == 5 else None,
                "status": "CLOSED" if issue_id == 3 else "OPEN",
                "category": "KEYPAD" if issue_id == 4 else "LIGHTING",
                "description": "通信が不安定" if issue_id == 6 else "照明が点滅する",
                "created_by": 1, "updated_by": 1,
                "created_at": timestamp,
                "updated_at": timestamp + timedelta(
                    hours=3 if issue_id == 7 else 2 if issue_id <= 2 else 1
                ),
            })
        connection.execute(Issue.__table__.insert(), issues)

    def database_session() -> Generator[Session, None, None]:
        with Session(database_engine) as session:
            yield session

    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[deps.get_db_session] = database_session
    application.dependency_overrides[deps.get_current_user] = lambda: CurrentUserResponse(
        id=1, username="engineer", display_name="Engineer", role="ENGINEER"
    )
    with TestClient(application) as client:
        yield client


@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        ({}, [2, 1, 6, 5, 4, 3]),
        ({"keyword": "照明"}, [2, 1, 5, 4, 3]),
        ({"status": "OPEN"}, [2, 1, 6, 5, 4]),
        ({"category": "LIGHTING"}, [2, 1, 6, 5, 3]),
        ({"target_type": "ROOM"}, [2, 1, 6, 4, 3]),
        ({"target_type": "OTHER"}, [5]),
        ({
            "keyword": "照明", "status": "OPEN",
            "category": "LIGHTING", "target_type": "ROOM",
        }, [2, 1]),
        ({"keyword": "該当なし"}, []),
    ],
    ids=["unfiltered", "keyword", "status", "category", "room", "other", "and", "empty"],
)
def test_search_returns_project_scoped_results_and_matching_total(
    search_client: TestClient, filters: dict[str, str], expected_ids: list[int]
) -> None:
    response = search_client.get("/api/projects/1/issues", params=filters)

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data["items"]] == expected_ids
    assert data["total"] == len(expected_ids)
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_filtered_pagination_preserves_total_and_order(search_client: TestClient) -> None:
    filters = {
        "keyword": "照明", "status": "OPEN", "category": "LIGHTING",
        "target_type": "ROOM", "page_size": 1,
    }
    for page, expected_ids in ((1, [2]), (2, [1]), (3, [])):
        response = search_client.get(
            "/api/projects/1/issues", params={**filters, "page": page}
        )

        assert response.status_code == 200
        data = response.json()
        assert [item["id"] for item in data["items"]] == expected_ids
        assert data["total"] == 2
        assert data["page"] == page
        assert data["page_size"] == 1
