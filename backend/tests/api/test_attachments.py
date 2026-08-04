"""Attachment API integration tests."""

from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_attachment_service, get_current_user
from app.core.config import Settings
from app.core.exceptions import NotFoundError, StorageError, ValidationError
from app.main import create_app
from app.schemas import AttachmentResponse, CurrentUserResponse, UploadAttachmentResponse

CURRENT_USER = CurrentUserResponse(
    id=7,
    username="engineer@example.com",
    display_name="Engineer",
    role="ENGINEER",
)


@pytest.fixture
def attachment_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(attachment_service) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    application.dependency_overrides[get_attachment_service] = lambda: attachment_service
    with TestClient(application) as test_client:
        yield test_client


def test_upload_attachment_returns_approved_response(client, attachment_service) -> None:
    attachment_service.upload_attachment.return_value = UploadAttachmentResponse(
        id=12, file_name="stored.jpg", message="Attachment uploaded"
    )

    response = client.post(
        "/api/issues/6/attachments",
        files={"file": ("photo.jpg", b"content", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 12,
        "file_name": "stored.jpg",
        "message": "Attachment uploaded",
    }
    issue_id, uploaded_file, user_id = (
        attachment_service.upload_attachment.call_args.args
    )
    assert issue_id == 6
    assert uploaded_file.filename == "photo.jpg"
    assert uploaded_file.content_type == "image/jpeg"
    assert user_id == 7


def test_upload_attachment_requires_exact_file_field(client, attachment_service) -> None:
    response = client.post(
        "/api/issues/6/attachments",
        files={"upload": ("photo.jpg", b"content", "image/jpeg")},
    )
    assert response.status_code == 400
    attachment_service.upload_attachment.assert_not_called()


@pytest.mark.parametrize(
    ("error", "status_code"),
    [(ValidationError(), 400), (NotFoundError(), 404)],
)
def test_upload_attachment_returns_service_errors(
    client, attachment_service, error, status_code
) -> None:
    attachment_service.upload_attachment.side_effect = error
    response = client.post(
        "/api/issues/999/attachments",
        files={"file": ("photo.jpg", b"content", "image/jpeg")},
    )
    assert response.status_code == status_code


def test_list_attachments_returns_only_approved_fields(
    client, attachment_service
) -> None:
    attachment_service.list_attachments.return_value = [
        AttachmentResponse(
            id=12,
            file_name="stored.jpg",
            mime_type="image/jpeg",
            file_size=7,
            uploaded_at=datetime(2026, 8, 4, 10, 20),
        )
    ]

    response = client.get("/api/issues/6/attachments")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 12,
                "file_name": "stored.jpg",
                "mime_type": "image/jpeg",
                "file_size": 7,
                "uploaded_at": "2026-08-04T10:20:00",
            }
        ]
    }
    attachment_service.list_attachments.assert_called_once_with(6)


def test_list_attachments_returns_empty_items(client, attachment_service) -> None:
    attachment_service.list_attachments.return_value = []
    assert client.get("/api/issues/6/attachments").json() == {"items": []}


def test_list_attachments_returns_missing_issue(client, attachment_service) -> None:
    attachment_service.list_attachments.side_effect = NotFoundError()
    assert client.get("/api/issues/999/attachments").status_code == 404


def test_download_attachment_returns_file_and_approved_headers(
    client, attachment_service, tmp_path: Path
) -> None:
    path = tmp_path / "stored.jpg"
    path.write_bytes(b"image-content")
    attachment_service.get_attachment_download.return_value = (
        path,
        "site photo.jpg",
        "image/jpeg",
    )

    response = client.get("/api/attachments/12")

    assert response.status_code == 200
    assert response.content == b"image-content"
    assert response.headers["content-type"] == "image/jpeg"
    disposition = response.headers["content-disposition"]
    assert disposition.startswith("inline;")
    assert "site%20photo.jpg" in disposition
    attachment_service.get_attachment_download.assert_called_once_with(12)


@pytest.mark.parametrize(
    ("error", "status_code"),
    [(NotFoundError(), 404), (StorageError(), 500)],
)
def test_download_attachment_returns_service_errors(
    client, attachment_service, error, status_code
) -> None:
    attachment_service.get_attachment_download.side_effect = error
    assert client.get("/api/attachments/99").status_code == status_code


def test_delete_attachment_returns_approved_response(client, attachment_service) -> None:
    response = client.delete("/api/issues/6/attachments/12")

    assert response.status_code == 200
    assert response.json() == {"message": "Attachment deleted"}
    attachment_service.delete_attachment.assert_called_once_with(6, 12, 7)


def test_delete_attachment_returns_not_found(client, attachment_service) -> None:
    attachment_service.delete_attachment.side_effect = NotFoundError()
    assert client.delete("/api/issues/6/attachments/99").status_code == 404


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("post", "/api/issues/6/attachments", {"files": {"file": ("a.jpg", b"x")}}),
        ("get", "/api/issues/6/attachments", {}),
        ("get", "/api/attachments/12", {}),
        ("delete", "/api/issues/6/attachments/12", {}),
    ],
)
def test_attachment_routes_require_authentication(method, path, kwargs) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    with TestClient(application) as unauthenticated_client:
        response = getattr(unauthenticated_client, method)(path, **kwargs)
    assert response.status_code == 401
