"""Room database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Room


class RoomRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, room_id: int) -> Room | None:
        return self.session.get(Room, room_id)

    def find_by_hotel_and_room_number(
        self, hotel_id: int, room_number: str
    ) -> Room | None:
        statement = select(Room).where(
            Room.hotel_id == hotel_id,
            Room.room_number == room_number,
        )
        return self.session.scalar(statement)

    def list_by_hotel(self, hotel_id: int) -> list[Room]:
        statement = (
            select(Room)
            .where(Room.hotel_id == hotel_id)
            .order_by(Room.id.asc())
        )
        return list(self.session.scalars(statement))
