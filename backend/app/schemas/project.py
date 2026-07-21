"""Project response schemas."""

from pydantic import BaseModel, ConfigDict

from app.schemas.common import HotelReferenceResponse


class ProjectResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    hotel: HotelReferenceResponse


class ProjectListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projects: list[ProjectResponse]
