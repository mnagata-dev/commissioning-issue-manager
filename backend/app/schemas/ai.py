"""AI draft request and response schemas."""

from pydantic import BaseModel, ConfigDict


class GenerateDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: int
    target_type: str
    room_id: int | None = None
    target: str | None = None
    input_text: str


class GenerateDraftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    description: str
