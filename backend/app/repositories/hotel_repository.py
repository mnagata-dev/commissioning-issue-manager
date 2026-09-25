"""Hotel database access."""

from sqlalchemy.orm import Session

from app.models import Hotel


class HotelRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, hotel_id: int) -> Hotel | None:
        return self.session.get(Hotel, hotel_id)
