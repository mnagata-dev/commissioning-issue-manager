"""Room response schemas."""

from pydantic import BaseModel, ConfigDict


class RoomResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    room_number: str
    display_name: str | None


class RoomListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rooms: list[RoomResponse]
