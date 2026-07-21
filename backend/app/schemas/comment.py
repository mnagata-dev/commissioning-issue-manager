"""Comment request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import UserReferenceResponse


class CreateCommentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comment: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    comment: str
    created_by: UserReferenceResponse
    created_at: datetime
