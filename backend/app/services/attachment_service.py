"""Attachment application service."""

from datetime import datetime, timezone
import logging
from pathlib import PurePath

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, StorageError, ValidationError
from app.models import Attachment, Issue, User
from app.repositories import AttachmentRepository, IssueRepository, UserRepository
from app.schemas import UploadAttachmentResponse
from app.services.storage_service import StorageService, StoredFile

logger = logging.getLogger(__name__)

_MIME_EXTENSIONS = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "video/mp4": {".mp4"},
    "video/quicktime": {".mov"},
}
_IMAGE_MAX_SIZE = 10 * 1024 * 1024
_VIDEO_MAX_SIZE = 100 * 1024 * 1024
_READ_CHUNK_SIZE = 1024 * 1024


class AttachmentService:
    def __init__(
        self,
        session: Session,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        attachment_repository: AttachmentRepository,
        storage_service: StorageService,
    ) -> None:
        self.session = session
        self.issue_repository = issue_repository
        self.user_repository = user_repository
        self.attachment_repository = attachment_repository
        self.storage_service = storage_service

    def upload_attachment(
        self, issue_id: int, file: UploadFile, user_id: int
    ) -> UploadAttachmentResponse:
        stored_file: StoredFile | None = None
        try:
            issue = self._require_issue(issue_id)
            user = self._require_user(user_id)
            original_file_name, maximum_size = self._validate_file(file)
            expected_size = self._measure_file(file, maximum_size)
            stored_file = self.storage_service.save_file(issue_id, file)
            if stored_file.file_size != expected_size:
                raise StorageError()
            attachment = Attachment(
                issue=issue,
                file_name=stored_file.file_name,
                original_file_name=original_file_name,
                file_path=stored_file.file_path,
                mime_type=stored_file.mime_type,
                file_size=stored_file.file_size,
                uploader=user,
                uploaded_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            created = self.attachment_repository.create(attachment)
            self.session.commit()
        except Exception as error:
            self.session.rollback()
            if stored_file is not None:
                try:
                    self.storage_service.delete_file(stored_file.file_path)
                except StorageError as cleanup_error:
                    logger.exception("Failed to compensate attachment upload.")
                    raise cleanup_error from error
            raise

        return UploadAttachmentResponse(
            id=created.id,
            file_name=created.file_name,
            message="Attachment uploaded",
        )

    def delete_attachment(
        self, issue_id: int, attachment_id: int, user_id: int
    ) -> None:
        staged_file = None
        try:
            self._require_issue(issue_id)
            self._require_user(user_id)
            attachment = self.attachment_repository.find_by_id(attachment_id)
            if attachment is None or attachment.issue_id != issue_id:
                raise NotFoundError("Attachment not found.")
            staged_file = self.storage_service.stage_file(attachment.file_path)
            self.attachment_repository.delete(attachment)
            self.session.commit()
        except Exception:
            self.session.rollback()
            if staged_file is not None:
                try:
                    self.storage_service.restore_file(staged_file)
                except StorageError:
                    logger.exception("Failed to restore staged attachment file.")
            raise

        if staged_file is not None:
            try:
                self.storage_service.purge_staged_file(staged_file)
            except StorageError:
                logger.exception("Failed to purge staged attachment file.")

    def _require_issue(self, issue_id: int) -> Issue:
        issue = self.issue_repository.find_by_id(issue_id)
        if issue is None:
            raise NotFoundError("Issue not found.")
        return issue

    def _require_user(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    @staticmethod
    def _validate_file(file: UploadFile) -> tuple[str, int]:
        file_name = file.filename
        if (
            file_name is None
            or file_name == ""
            or PurePath(file_name).is_absolute()
            or "/" in file_name
            or "\\" in file_name
            or any(ord(character) < 32 or ord(character) == 127 for character in file_name)
        ):
            raise ValidationError("Invalid attachment file name.")

        extension = PurePath(file_name).suffix.lower()
        content_type = file.content_type
        if content_type not in _MIME_EXTENSIONS:
            raise ValidationError("Invalid attachment file type.")
        if extension not in _MIME_EXTENSIONS[content_type]:
            raise ValidationError("Attachment MIME type and extension do not match.")
        maximum_size = (
            _IMAGE_MAX_SIZE if content_type.startswith("image/") else _VIDEO_MAX_SIZE
        )
        return file_name, maximum_size

    @staticmethod
    def _measure_file(file: UploadFile, maximum_size: int) -> int:
        try:
            file.file.seek(0)
            size = 0
            while chunk := file.file.read(_READ_CHUNK_SIZE):
                size += len(chunk)
                if size > maximum_size:
                    raise ValidationError("Attachment file is too large.")
            file.file.seek(0)
        except ValidationError:
            file.file.seek(0)
            raise
        except (OSError, ValueError) as error:
            raise StorageError() from error
        if size == 0:
            raise ValidationError("Attachment file must not be empty.")
        return size
