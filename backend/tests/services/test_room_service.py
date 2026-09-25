from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from app.core.exceptions import NotFoundError
from app.repositories import HotelRepository, RoomRepository
from app.services import RoomService


@pytest.mark.parametrize("empty", [False, True])
def test_list_rooms_preserves_order_without_transaction(domain_entities, empty) -> None:
    session = MagicMock()
    hotels = MagicMock(spec=HotelRepository)
    rooms = MagicMock(spec=RoomRepository)
    hotels.session = rooms.session = session
    hotels.find_by_id.return_value = domain_entities["hotel"]
    rooms.list_by_hotel.return_value = [] if empty else [
        SimpleNamespace(id=9, room_number="1205", display_name="Suite"),
        domain_entities["room"],
    ]
    calls = MagicMock()
    calls.attach_mock(hotels.find_by_id, "find_hotel")
    calls.attach_mock(rooms.list_by_hotel, "list_rooms")

    response = RoomService(hotels, rooms).list_rooms(1)

    assert response.model_dump() == {"rooms": [] if empty else [
        {"id": 9, "room_number": "1205", "display_name": "Suite"},
        {"id": 4, "room_number": "1203", "display_name": None},
    ]}
    assert calls.mock_calls == [call.find_hotel(1), call.list_rooms(1)]
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_hotel_not_found_does_not_query_rooms() -> None:
    hotels = MagicMock(spec=HotelRepository)
    rooms = MagicMock(spec=RoomRepository)
    hotels.find_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Hotel not found"):
        RoomService(hotels, rooms).list_rooms(99)

    hotels.find_by_id.assert_called_once_with(99)
    rooms.list_by_hotel.assert_not_called()
