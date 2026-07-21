"""Shared nested response schemas."""

from pydantic import BaseModel, ConfigDict


class HotelReferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str


class ProjectReferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str


class RoomReferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    room_number: str


class UserReferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    display_name: str
