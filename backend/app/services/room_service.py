"""Room application service."""

from app.core.exceptions import NotFoundError
from app.repositories import HotelRepository, RoomRepository
from app.schemas import RoomListResponse, RoomResponse


class RoomService:
    def __init__(
        self, hotel_repository: HotelRepository, room_repository: RoomRepository
    ) -> None:
        self.hotel_repository = hotel_repository
        self.room_repository = room_repository

    def list_rooms(self, hotel_id: int) -> RoomListResponse:
        if self.hotel_repository.find_by_id(hotel_id) is None:
            raise NotFoundError("Hotel not found.")
        rooms = self.room_repository.list_by_hotel(hotel_id)
        return RoomListResponse(
            rooms=[
                RoomResponse(
                    id=room.id,
                    room_number=room.room_number,
                    display_name=room.display_name,
                )
                for room in rooms
            ]
        )
