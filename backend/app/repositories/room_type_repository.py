"""Room type database access."""

from sqlalchemy.orm import Session

from app.models import RoomType


class RoomTypeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, room_type_id: int) -> RoomType | None:
        return self.session.get(RoomType, room_type_id)

    def create(self, room_type: RoomType) -> RoomType:
        self.session.add(room_type)
        self.session.flush()
        return room_type

    def update(self, room_type: RoomType) -> RoomType:
        self.session.flush()
        return room_type
