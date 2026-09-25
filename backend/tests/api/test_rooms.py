from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user, get_room_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.main import create_app
from app.repositories import HotelRepository, RoomRepository
from app.schemas import CurrentUserResponse, RoomListResponse
from app.services import RoomService


@pytest.fixture
def service() -> MagicMock:
    return MagicMock(spec=RoomService)


@pytest.fixture
def client(service) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CurrentUserResponse(
        id=7, username="engineer", display_name="Engineer", role="ENGINEER"
    )
    application.dependency_overrides[get_room_service] = lambda: service
    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.parametrize("rooms", [
    [],
    [{"id": 4, "room_number": "1203", "display_name": None},
     {"id": 5, "room_number": "1205", "display_name": "Suite"}],
])
def test_list_rooms_returns_service_response(client, service, rooms) -> None:
    service.list_rooms.return_value = RoomListResponse(rooms=rooms)

    response = client.get("/api/hotels/1/rooms")

    assert response.status_code == 200
    assert response.json() == {"rooms": rooms}
    service.list_rooms.assert_called_once_with(1)


def test_missing_hotel_returns_common_error(client, service) -> None:
    service.list_rooms.side_effect = NotFoundError("Hotel not found.")

    response = client.get("/api/hotels/99/rooms")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NOT_FOUND_ERROR", "message": "Hotel not found."}
    }


def test_rooms_require_authentication(service) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_room_service] = lambda: service
    with TestClient(application) as client:
        response = client.get("/api/hotels/1/rooms")

    assert response.status_code == 401
    service.list_rooms.assert_not_called()


def test_invalid_hotel_id_is_safe_validation_error(client, service) -> None:
    response = client.get("/api/hotels/invalid/rooms")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    service.list_rooms.assert_not_called()


def test_room_dependency_uses_same_session() -> None:
    session = MagicMock()

    service = get_room_service(session)

    assert isinstance(service.hotel_repository, HotelRepository)
    assert isinstance(service.room_repository, RoomRepository)
    assert service.hotel_repository.session is session
    assert service.room_repository.session is session
