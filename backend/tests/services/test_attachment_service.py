from datetime import datetime
from io import BytesIO
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.exceptions import NotFoundError, StorageError, ValidationError
from app.services import AttachmentService
from app.services.storage_service import StoredFile


def upload(
    filename: str | None, content_type: str, content: bytes = b"content"
) -> UploadFile:
    return UploadFile(
        BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def ordered_calls(*mocks: tuple[str, MagicMock]) -> MagicMock:
    calls = MagicMock()
    for name, mock in mocks:
        calls.attach_mock(mock, name)
    return calls


@pytest.fixture
def repositories(domain_entities):
    issue_repository = MagicMock()
    user_repository = MagicMock()
    attachment_repository = MagicMock()
    issue_repository.find_by_id.return_value = domain_entities["issue"]
    user_repository.find_by_id.return_value = domain_entities["user"]
    domain_entities["attachment"].issue_id = domain_entities["issue"].id
    attachment_repository.find_by_id.return_value = domain_entities["attachment"]
    return issue_repository, user_repository, attachment_repository


@pytest.fixture
def storage_service() -> MagicMock:
    storage = MagicMock()
    storage.save_file.return_value = StoredFile(
        file_name="550e8400-e29b-41d4-a716-446655440000.jpg",
        file_path=(
            "attachments/issues/6/550e8400-e29b-41d4-a716-446655440000.jpg"
        ),
        mime_type="image/jpeg",
        file_size=7,
    )
    return storage


@pytest.fixture
def service(session, repositories, storage_service) -> AttachmentService:
    return AttachmentService(session, *repositories, storage_service)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("photo.jpg", "image/jpeg"),
        ("photo.JPEG", "image/jpeg"),
        ("photo.png", "image/png"),
        ("video.mp4", "video/mp4"),
        ("video.mov", "video/quicktime"),
    ],
)
def test_upload_success_sets_metadata_and_commits(
    service,
    session,
    repositories,
    storage_service,
    domain_entities,
    filename,
    content_type,
) -> None:
    _, _, attachment_repository = repositories
    stored = storage_service.save_file.return_value
    stored = StoredFile(
        stored.file_name,
        stored.file_path,
        content_type,
        stored.file_size,
    )
    storage_service.save_file.return_value = stored

    def assign_id(attachment):
        attachment.id = 15
        return attachment

    attachment_repository.create.side_effect = assign_id
    calls = ordered_calls(
        ("storage", storage_service),
        ("attachment", attachment_repository),
        ("session", session),
    )

    result = service.upload_attachment(6, upload(filename, content_type), 3)

    assert result.model_dump() == {
        "id": 15,
        "file_name": stored.file_name,
        "message": "Attachment uploaded",
    }
    created = attachment_repository.create.call_args.args[0]
    assert created.issue is domain_entities["issue"]
    assert created.uploader is domain_entities["user"]
    assert created.original_file_name == filename
    assert created.file_path == stored.file_path
    assert created.mime_type == content_type
    assert created.file_size == 7
    assert created.uploaded_at.tzinfo is None
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()
    call_names = [call[0] for call in calls.mock_calls]
    assert call_names.index("storage.save_file") < call_names.index(
        "attachment.create"
    ) < call_names.index("session.commit")


def test_upload_missing_issue_or_user(
    service, session, repositories, storage_service
) -> None:
    issue_repository, user_repository, _ = repositories
    issue_repository.find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="Issue not found"):
        service.upload_attachment(99, upload("photo.jpg", "image/jpeg"), 3)
    storage_service.save_file.assert_not_called()

    issue_repository.find_by_id.reset_mock()
    issue_repository.find_by_id.return_value = MagicMock()
    user_repository.find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="User not found"):
        service.upload_attachment(6, upload("photo.jpg", "image/jpeg"), 99)
    assert session.rollback.call_count == 2


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        (None, "image/jpeg"),
        ("", "image/jpeg"),
        ("../photo.jpg", "image/jpeg"),
        ("folder/photo.jpg", "image/jpeg"),
        (r"folder\\photo.jpg", "image/jpeg"),
        ("bad\x00.jpg", "image/jpeg"),
        ("photo.gif", "image/gif"),
        ("photo.gif", "image/jpeg"),
        ("photo.jpg", "image/png"),
    ],
)
def test_upload_rejects_invalid_name_or_type_without_saving(
    service, storage_service, filename, content_type
) -> None:
    with pytest.raises(ValidationError):
        service.upload_attachment(6, upload(filename, content_type), 3)
    storage_service.save_file.assert_not_called()


@pytest.mark.parametrize(
    ("filename", "content_type", "size"),
    [
        ("empty.jpg", "image/jpeg", 0),
        ("large.png", "image/png", 10 * 1024 * 1024 + 1),
        ("large.mp4", "video/mp4", 100 * 1024 * 1024 + 1),
    ],
)
def test_upload_rejects_empty_or_oversized_file(
    service, storage_service, filename, content_type, size
) -> None:
    with pytest.raises(ValidationError):
        service.upload_attachment(6, upload(filename, content_type, b"x" * size), 3)
    storage_service.save_file.assert_not_called()


def test_upload_accepts_exact_size_limits(service, storage_service, repositories) -> None:
    attachment_repository = repositories[2]
    attachment_repository.create.side_effect = (
        lambda attachment: setattr(attachment, "id", 1) or attachment
    )
    for filename, content_type, size in (
        ("image.jpg", "image/jpeg", 10 * 1024 * 1024),
        ("video.mp4", "video/mp4", 100 * 1024 * 1024),
    ):
        stored = storage_service.save_file.return_value
        storage_service.save_file.return_value = StoredFile(
            stored.file_name, stored.file_path, content_type, size
        )
        service.upload_attachment(6, upload(filename, content_type, b"x" * size), 3)


def test_upload_storage_failure_creates_no_metadata(
    service, repositories, storage_service
) -> None:
    storage_service.save_file.side_effect = StorageError()
    with pytest.raises(StorageError):
        service.upload_attachment(6, upload("photo.jpg", "image/jpeg"), 3)
    repositories[2].create.assert_not_called()


@pytest.mark.parametrize("failure_point", ["create", "commit"])
def test_upload_db_failure_rolls_back_and_compensates(
    service, session, repositories, storage_service, failure_point
) -> None:
    if failure_point == "create":
        repositories[2].create.side_effect = RuntimeError("database")
    else:
        repositories[2].create.side_effect = (
            lambda attachment: setattr(attachment, "id", 1) or attachment
        )
        session.commit.side_effect = RuntimeError("database")
    calls = ordered_calls(("session", session), ("storage", storage_service))

    with pytest.raises(RuntimeError, match="database"):
        service.upload_attachment(6, upload("photo.jpg", "image/jpeg"), 3)

    session.rollback.assert_called_once_with()
    storage_service.delete_file.assert_called_once_with(
        storage_service.save_file.return_value.file_path
    )
    call_names = [call[0] for call in calls.mock_calls]
    assert call_names.index("session.rollback") < call_names.index(
        "storage.delete_file"
    )


def test_upload_compensation_failure_prioritizes_storage_error(
    service, session, repositories, storage_service, caplog
) -> None:
    repositories[2].create.side_effect = RuntimeError("database")
    storage_service.delete_file.side_effect = StorageError()
    with caplog.at_level(logging.ERROR):
        with pytest.raises(StorageError):
            service.upload_attachment(6, upload("photo.jpg", "image/jpeg"), 3)
    session.rollback.assert_called_once_with()
    assert any(
        record.levelno >= logging.ERROR
        and "compensate attachment upload" in record.getMessage().lower()
        for record in caplog.records
    )


def test_list_attachments_preserves_order_and_converts_dtos(
    service, session, repositories, domain_entities
) -> None:
    first = domain_entities["attachment"]
    first.id = 8
    first.file_name = "first.jpg"
    first.mime_type = "image/jpeg"
    first.file_size = 10
    first.uploaded_at = datetime(2026, 8, 4, 10, 20)
    second = MagicMock(
        id=9,
        file_name="second.mp4",
        mime_type="video/mp4",
        file_size=20,
        uploaded_at=datetime(2026, 8, 4, 10, 21),
    )
    repositories[2].list_by_issue.return_value = [first, second]

    result = service.list_attachments(6)

    assert [item.id for item in result] == [8, 9]
    assert result[0].model_dump() == {
        "id": 8,
        "file_name": "first.jpg",
        "mime_type": "image/jpeg",
        "file_size": 10,
        "uploaded_at": datetime(2026, 8, 4, 10, 20),
    }
    repositories[2].list_by_issue.assert_called_once_with(6)
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_list_attachments_returns_empty_list(service, session, repositories) -> None:
    repositories[2].list_by_issue.return_value = []

    assert service.list_attachments(6) == []
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_list_attachments_requires_issue(service, session, repositories) -> None:
    repositories[0].find_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Issue not found"):
        service.list_attachments(99)

    repositories[2].list_by_issue.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_get_attachment_download_returns_approved_tuple(
    service, session, repositories, storage_service
) -> None:
    attachment = repositories[2].find_by_id.return_value
    attachment.file_path = "attachments/issues/6/stored.jpg"
    attachment.original_file_name = "photo.jpg"
    attachment.mime_type = "image/jpeg"
    resolved = Path("/safe/storage/attachments/issues/6/stored.jpg")
    storage_service.resolve_file.return_value = resolved

    result = service.get_attachment_download(attachment.id)

    assert result == (resolved, "photo.jpg", "image/jpeg")
    storage_service.resolve_file.assert_called_once_with(attachment.file_path)
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_get_attachment_download_handles_missing_metadata(
    service, session, repositories, storage_service
) -> None:
    repositories[2].find_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Attachment not found"):
        service.get_attachment_download(99)

    storage_service.resolve_file.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_get_attachment_download_handles_missing_file(
    service, session, repositories, storage_service
) -> None:
    storage_service.resolve_file.return_value = None

    with pytest.raises(NotFoundError, match="Attachment file not found"):
        service.get_attachment_download(8)

    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_delete_success_stages_commits_and_purges(
    service, session, repositories, storage_service
) -> None:
    staged = MagicMock()
    storage_service.stage_file.return_value = staged
    calls = ordered_calls(
        ("storage", storage_service),
        ("attachment", repositories[2]),
        ("session", session),
    )

    service.delete_attachment(6, 8, 3)

    storage_service.stage_file.assert_called_once_with(
        repositories[2].find_by_id.return_value.file_path
    )
    repositories[2].delete.assert_called_once_with(
        repositories[2].find_by_id.return_value
    )
    session.commit.assert_called_once_with()
    storage_service.purge_staged_file.assert_called_once_with(staged)
    call_names = [call[0] for call in calls.mock_calls]
    assert call_names.index("storage.stage_file") < call_names.index(
        "attachment.delete"
    ) < call_names.index("session.commit") < call_names.index(
        "storage.purge_staged_file"
    )


def test_delete_missing_physical_file_continues_metadata_delete(
    service, session, repositories, storage_service
) -> None:
    storage_service.stage_file.return_value = None
    service.delete_attachment(6, 8, 3)
    repositories[2].delete.assert_called_once()
    session.commit.assert_called_once()
    storage_service.purge_staged_file.assert_not_called()


def test_delete_validates_resources_and_ownership(
    service, repositories, storage_service
) -> None:
    issue_repository, user_repository, attachment_repository = repositories
    issue_repository.find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="Issue not found"):
        service.delete_attachment(99, 8, 3)

    issue_repository.find_by_id.return_value = MagicMock()
    user_repository.find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="User not found"):
        service.delete_attachment(6, 8, 99)

    user_repository.find_by_id.return_value = MagicMock()
    attachment_repository.find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="Attachment not found"):
        service.delete_attachment(6, 99, 3)

    attachment_repository.find_by_id.return_value = MagicMock(issue_id=99)
    with pytest.raises(NotFoundError, match="Attachment not found"):
        service.delete_attachment(6, 8, 3)
    storage_service.stage_file.assert_not_called()


def test_delete_staging_failure_does_not_delete_metadata(
    service, session, repositories, storage_service
) -> None:
    storage_service.stage_file.side_effect = StorageError()
    with pytest.raises(StorageError):
        service.delete_attachment(6, 8, 3)
    repositories[2].delete.assert_not_called()
    session.rollback.assert_called_once()


@pytest.mark.parametrize("failure_point", ["delete", "commit"])
def test_delete_db_failure_rolls_back_and_restores(
    service, session, repositories, storage_service, failure_point
) -> None:
    staged = MagicMock()
    storage_service.stage_file.return_value = staged
    if failure_point == "delete":
        repositories[2].delete.side_effect = RuntimeError("database")
    else:
        session.commit.side_effect = RuntimeError("database")
    calls = ordered_calls(("session", session), ("storage", storage_service))

    with pytest.raises(RuntimeError, match="database"):
        service.delete_attachment(6, 8, 3)

    session.rollback.assert_called_once()
    storage_service.restore_file.assert_called_once_with(staged)
    storage_service.purge_staged_file.assert_not_called()
    call_names = [call[0] for call in calls.mock_calls]
    assert call_names.index("session.rollback") < call_names.index(
        "storage.restore_file"
    )


def test_delete_restore_failure_preserves_original_db_error(
    service, session, repositories, storage_service, caplog
) -> None:
    storage_service.stage_file.return_value = MagicMock()
    repositories[2].delete.side_effect = RuntimeError("database")
    storage_service.restore_file.side_effect = StorageError()
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="database"):
            service.delete_attachment(6, 8, 3)
    session.rollback.assert_called_once()
    assert any(
        record.levelno >= logging.ERROR
        and "restore staged attachment" in record.getMessage().lower()
        for record in caplog.records
    )


def test_delete_trash_purge_failure_keeps_committed_success(
    service, session, storage_service, caplog
) -> None:
    storage_service.stage_file.return_value = MagicMock()
    storage_service.purge_staged_file.side_effect = StorageError()
    with caplog.at_level(logging.ERROR):
        service.delete_attachment(6, 8, 3)
    session.commit.assert_called_once()
    assert any(
        record.levelno >= logging.ERROR
        and "purge staged attachment" in record.getMessage().lower()
        for record in caplog.records
    )
