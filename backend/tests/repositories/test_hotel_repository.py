from sqlalchemy.orm import Session

from app.repositories import HotelRepository


def test_find_hotel_by_id(database_session: Session, base_entities) -> None:
    repository = HotelRepository(database_session)
    hotel = base_entities["hotel"]

    assert repository.find_by_id(hotel.id) is hotel
    assert repository.find_by_id(99999) is None
