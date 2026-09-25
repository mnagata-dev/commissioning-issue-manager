"""Room API routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUserDependency, RoomServiceDependency
from app.schemas import RoomListResponse

router = APIRouter(prefix="/api/hotels", tags=["rooms"])


@router.get("/{hotel_id}/rooms", response_model=RoomListResponse)
def list_rooms(
    hotel_id: int,
    current_user: CurrentUserDependency,
    room_service: RoomServiceDependency,
) -> RoomListResponse:
    del current_user
    return room_service.list_rooms(hotel_id)
