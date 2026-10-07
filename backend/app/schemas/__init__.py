"""Pydantic schema package."""

from app.schemas.ai import GenerateDraftRequest, GenerateDraftResponse
from app.schemas.attachment import AttachmentResponse, UploadAttachmentResponse
from app.schemas.auth import CurrentUserResponse, LoginRequest
from app.schemas.comment import CommentResponse, CreateCommentRequest
from app.schemas.common import (
    HotelReferenceResponse,
    ProjectReferenceResponse,
    RoomReferenceResponse,
    UserReferenceResponse,
)
from app.schemas.issue import (
    CreateIssueRequest,
    IssueDetailResponse,
    IssueListResponse,
    IssueSummaryResponse,
    UpdateIssueRequest,
    UpdateIssueStatusRequest,
)
from app.schemas.project import ProjectListResponse, ProjectResponse
from app.schemas.room import RoomListResponse, RoomResponse
from app.schemas.speech import SpeechTranscriptionResponse

__all__ = [
    "AttachmentResponse",
    "CommentResponse",
    "CreateCommentRequest",
    "CreateIssueRequest",
    "CurrentUserResponse",
    "GenerateDraftRequest",
    "GenerateDraftResponse",
    "HotelReferenceResponse",
    "IssueDetailResponse",
    "IssueListResponse",
    "IssueSummaryResponse",
    "LoginRequest",
    "ProjectListResponse",
    "ProjectReferenceResponse",
    "ProjectResponse",
    "RoomReferenceResponse",
    "RoomListResponse",
    "RoomResponse",
    "SpeechTranscriptionResponse",
    "UpdateIssueRequest",
    "UpdateIssueStatusRequest",
    "UploadAttachmentResponse",
    "UserReferenceResponse",
]
