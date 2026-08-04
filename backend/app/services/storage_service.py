"""Local attachment file storage."""

from dataclasses import dataclass
from pathlib import Path
import stat
from uuid import uuid4

from fastapi import UploadFile

from app.core.exceptions import StorageError


@dataclass(frozen=True, slots=True)
class StoredFile:
    """Metadata for a file saved beneath the storage root."""

    file_name: str
    file_path: str
    mime_type: str
    file_size: int


@dataclass(frozen=True, slots=True)
class _StagedFile:
    original_path: str
    trash_path: str


class StorageService:
    """Store attachment files beneath a configured local root."""

    def __init__(self, storage_root: str | Path) -> None:
        self.storage_root = Path(storage_root).resolve()

    def save_file(self, issue_id: int, file: UploadFile) -> StoredFile:
        extension = Path(file.filename or "").suffix.lower()
        file_name = f"{uuid4()}{extension}"
        relative_path = Path("attachments", "issues", str(issue_id), file_name)
        destination = self._resolve_relative(relative_path)
        destination_created = False

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            file.file.seek(0)
            file_size = 0
            with destination.open("xb") as output:
                destination_created = True
                while chunk := file.file.read(1024 * 1024):
                    output.write(chunk)
                    file_size += len(chunk)
        except (OSError, ValueError) as error:
            if destination_created:
                try:
                    destination.unlink(missing_ok=True)
                except OSError:
                    pass
            raise StorageError() from error

        return StoredFile(
            file_name=file_name,
            file_path=relative_path.as_posix(),
            mime_type=file.content_type or "",
            file_size=file_size,
        )

    def delete_file(self, file_path: str) -> None:
        path = self._resolve_relative(file_path)
        try:
            path.unlink(missing_ok=True)
        except OSError as error:
            raise StorageError() from error

    def resolve_file(self, file_path: str) -> Path | None:
        try:
            relative_path = Path(file_path)
            if relative_path.is_absolute():
                raise StorageError()
            resolved = (self.storage_root / relative_path).resolve()
            if not resolved.is_relative_to(self.storage_root):
                raise StorageError()
            file_stat = resolved.stat()
        except FileNotFoundError:
            return None
        except StorageError:
            raise
        except (OSError, RuntimeError, ValueError) as error:
            raise StorageError() from error
        if not stat.S_ISREG(file_stat.st_mode):
            raise StorageError()
        return resolved

    def stage_file(self, file_path: str) -> _StagedFile | None:
        source = self._resolve_relative(file_path)
        try:
            source.stat()
        except FileNotFoundError:
            return None
        except OSError as error:
            raise StorageError() from error

        trash_relative = Path(".trash", f"{uuid4()}{source.suffix.lower()}")
        trash_path = self._resolve_relative(trash_relative)
        try:
            trash_path.parent.mkdir(parents=True, exist_ok=True)
            source.replace(trash_path)
        except OSError as error:
            raise StorageError() from error
        return _StagedFile(file_path, trash_relative.as_posix())

    def restore_file(self, staged_file: _StagedFile) -> None:
        source = self._resolve_relative(staged_file.trash_path)
        destination = self._resolve_relative(staged_file.original_path)
        try:
            if destination.exists():
                raise OSError("Attachment destination already exists.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
        except OSError as error:
            raise StorageError() from error

    def purge_staged_file(self, staged_file: _StagedFile) -> None:
        self.delete_file(staged_file.trash_path)

    def _resolve_relative(self, file_path: str | Path) -> Path:
        relative_path = Path(file_path)
        if relative_path.is_absolute():
            raise StorageError()
        resolved = (self.storage_root / relative_path).resolve()
        if not resolved.is_relative_to(self.storage_root):
            raise StorageError()
        return resolved
