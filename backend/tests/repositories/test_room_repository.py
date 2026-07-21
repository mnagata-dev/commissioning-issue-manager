from sqlalchemy.orm import Session

from app.repositories import RoomRepository


def test_find_and_list_rooms(database_session: Session, base_entities) -> None:
    repository = RoomRepository(database_session)
    room = base_entities["room"]
    hotel = base_entities["hotel"]
    assert repository.find_by_id(room.id) is room
    assert repository.find_by_id(99999) is None
    assert repository.find_by_hotel_and_room_number(hotel.id, "101") is room
    assert repository.find_by_hotel_and_room_number(hotel.id, "999") is None
    assert repository.list_by_hotel(hotel.id) == [room]
    assert base_entities["other_room"] not in repository.list_by_hotel(hotel.id)
