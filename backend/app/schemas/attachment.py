"""Attachment response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    file_name: str
    mime_type: str
    file_size: int
    uploaded_at: datetime


class UploadAttachmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    file_name: str
    message: str
