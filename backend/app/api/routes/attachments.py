"""Attachment API routes."""

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import AttachmentServiceDependency, CurrentUserDependency
from app.schemas import AttachmentResponse, UploadAttachmentResponse

router = APIRouter(tags=["attachments"])


@router.post("/api/issues/{issue_id}/attachments")
def upload_attachment(
    issue_id: int,
    current_user: CurrentUserDependency,
    attachment_service: AttachmentServiceDependency,
    file: UploadFile = File(...),
) -> UploadAttachmentResponse:
    return attachment_service.upload_attachment(issue_id, file, current_user.id)


@router.get("/api/issues/{issue_id}/attachments")
def list_attachments(
    issue_id: int,
    current_user: CurrentUserDependency,
    attachment_service: AttachmentServiceDependency,
) -> dict[str, list[AttachmentResponse]]:
    del current_user
    return {"items": attachment_service.list_attachments(issue_id)}


@router.get("/api/attachments/{attachment_id}", response_class=FileResponse)
def download_attachment(
    attachment_id: int,
    current_user: CurrentUserDependency,
    attachment_service: AttachmentServiceDependency,
) -> FileResponse:
    del current_user
    file_path, original_file_name, mime_type = (
        attachment_service.get_attachment_download(attachment_id)
    )
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=original_file_name,
        content_disposition_type="inline",
    )


@router.delete("/api/issues/{issue_id}/attachments/{attachment_id}")
def delete_attachment(
    issue_id: int,
    attachment_id: int,
    current_user: CurrentUserDependency,
    attachment_service: AttachmentServiceDependency,
) -> dict[str, str]:
    attachment_service.delete_attachment(issue_id, attachment_id, current_user.id)
    return {"message": "Attachment deleted"}
