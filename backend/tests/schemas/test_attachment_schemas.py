from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import AttachmentResponse, UploadAttachmentResponse


def test_attachment_response_accepts_valid_input() -> None:
    uploaded_at = datetime(2026, 7, 21, 10, 0)
    response = AttachmentResponse(
        id=1,
        file_name="photo.jpg",
        mime_type="image/jpeg",
        file_size=2048,
        uploaded_at=uploaded_at,
    )
    assert response.uploaded_at == uploaded_at


def test_upload_attachment_response_accepts_valid_input() -> None:
    response = UploadAttachmentResponse(
        id=1, file_name="photo.jpg", message="Attachment uploaded"
    )
    assert response.file_name == "photo.jpg"


def test_upload_attachment_response_requires_file_name() -> None:
    with pytest.raises(ValidationError):
        UploadAttachmentResponse.model_validate({"id": 1, "message": "Uploaded"})


@pytest.mark.parametrize(
    ("schema", "data"),
    [
        (AttachmentResponse, {"id": 1}),
        (UploadAttachmentResponse, {"id": 1, "file_name": "a.jpg"}),
    ],
)
def test_attachment_schemas_require_fields(schema, data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate(data)


def test_attachment_schemas_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        UploadAttachmentResponse(
            id=1, file_name="photo.jpg", message="Uploaded", file_path="internal/photo.jpg"
        )
