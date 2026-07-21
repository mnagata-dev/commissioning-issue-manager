"""Issue request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.attachment import AttachmentResponse
from app.schemas.comment import CommentResponse
from app.schemas.common import (
    ProjectReferenceResponse,
    RoomReferenceResponse,
    UserReferenceResponse,
)


class CreateIssueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: int | None = None
    target_type: str
    target: str | None = None
    category: str
    description: str


class UpdateIssueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: int | None
    target_type: str
    target: str | None
    category: str
    description: str


class UpdateIssueStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str


class IssueSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    room: RoomReferenceResponse | None
    target_type: str
    target: str | None
    category: str
    description: str
    status: str
    updated_at: datetime


class IssueDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    project: ProjectReferenceResponse
    room: RoomReferenceResponse | None
    target_type: str
    target: str | None
    category: str
    description: str
    status: str
    created_by: UserReferenceResponse
    updated_by: UserReferenceResponse
    created_at: datetime
    updated_at: datetime
    comments: list[CommentResponse]
    attachments: list[AttachmentResponse]
