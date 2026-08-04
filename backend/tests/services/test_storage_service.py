from io import BytesIO
from pathlib import Path
import re

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.exceptions import StorageError
from app.services.storage_service import StorageService


def upload(filename: str, content_type: str, content: bytes) -> UploadFile:
    return UploadFile(
        BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [("PHOTO.JPG", "image/jpeg"), ("video.MP4", "video/mp4")],
)
def test_save_file_preserves_content_and_returns_metadata(
    tmp_path: Path, filename: str, content_type: str
) -> None:
    service = StorageService(tmp_path)
    content = b"attachment-content"

    stored = service.save_file(12, upload(filename, content_type, content))

    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-"
        r"[0-9a-f]{12}\.(jpg|mp4)",
        stored.file_name,
    )
    assert stored.file_path == f"attachments/issues/12/{stored.file_name}"
    assert stored.mime_type == content_type
    assert stored.file_size == len(content)
    assert (tmp_path / stored.file_path).read_bytes() == content


def test_save_file_creates_unique_names(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    first = service.save_file(1, upload("same.png", "image/png", b"first"))
    second = service.save_file(1, upload("same.png", "image/png", b"second"))
    assert first.file_name != second.file_name


def test_delete_file_only_deletes_target(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    first = service.save_file(1, upload("one.jpg", "image/jpeg", b"one"))
    second = service.save_file(1, upload("two.jpg", "image/jpeg", b"two"))

    service.delete_file(first.file_path)

    assert not (tmp_path / first.file_path).exists()
    assert (tmp_path / second.file_path).exists()


def test_resolve_file_returns_regular_file_below_root(tmp_path: Path) -> None:
    target = tmp_path / "attachments/issues/1/photo.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"content")

    result = StorageService(tmp_path).resolve_file(
        "attachments/issues/1/photo.jpg"
    )

    assert result == target.resolve()
    assert result.is_relative_to(tmp_path.resolve())


def test_resolve_file_does_not_open_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "photo.jpg"
    target.write_bytes(b"content")

    def fail_open(*args, **kwargs):
        raise AssertionError("resolve_file must not open the file")

    monkeypatch.setattr(Path, "open", fail_open)
    assert StorageService(tmp_path).resolve_file("photo.jpg") == target.resolve()


def test_resolve_file_returns_none_for_missing_target(tmp_path: Path) -> None:
    assert StorageService(tmp_path).resolve_file("missing.jpg") is None


@pytest.mark.parametrize(
    "file_path",
    ["../outside.jpg", "/tmp/outside.jpg", "attachments/../../outside.jpg"],
)
def test_resolve_file_rejects_paths_outside_root(
    tmp_path: Path, file_path: str
) -> None:
    with pytest.raises(StorageError):
        StorageService(tmp_path).resolve_file(file_path)


def test_resolve_file_rejects_directory(tmp_path: Path) -> None:
    (tmp_path / "directory").mkdir()
    with pytest.raises(StorageError):
        StorageService(tmp_path).resolve_file("directory")


def test_resolve_file_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside.jpg"
    outside.write_bytes(b"outside")
    link = tmp_path / "link.jpg"
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError):
        pytest.skip("Symbolic links are not supported")

    with pytest.raises(StorageError):
        StorageService(tmp_path).resolve_file("link.jpg")


def test_resolve_file_converts_filesystem_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "photo.jpg"
    target.write_bytes(b"content")
    original_stat = Path.stat

    def fail_target_stat(path, *args, **kwargs):
        if path == target.resolve():
            raise OSError("private operating system detail")
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", fail_target_stat)
    with pytest.raises(StorageError) as error:
        StorageService(tmp_path).resolve_file("photo.jpg")
    assert str(error.value) == "The storage operation failed."


def test_stage_restore_and_purge(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    stored = service.save_file(1, upload("one.mov", "video/quicktime", b"video"))

    staged = service.stage_file(stored.file_path)

    assert staged is not None
    assert not (tmp_path / stored.file_path).exists()
    assert (tmp_path / staged.trash_path).read_bytes() == b"video"

    service.restore_file(staged)
    assert (tmp_path / stored.file_path).read_bytes() == b"video"

    staged = service.stage_file(stored.file_path)
    assert staged is not None
    service.purge_staged_file(staged)
    assert not (tmp_path / staged.trash_path).exists()


def test_stage_missing_file_is_successful_noop(tmp_path: Path) -> None:
    assert StorageService(tmp_path).stage_file("attachments/issues/1/missing.jpg") is None


@pytest.mark.parametrize(
    "file_path",
    ["../outside.jpg", "/tmp/outside.jpg", "attachments/../../outside.jpg"],
)
def test_paths_cannot_escape_storage_root(tmp_path: Path, file_path: str) -> None:
    with pytest.raises(StorageError):
        StorageService(tmp_path).delete_file(file_path)


def test_storage_io_failure_raises_safe_storage_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = StorageService(tmp_path)

    def fail_open(*args, **kwargs):
        raise OSError("private operating system detail")

    monkeypatch.setattr(Path, "open", fail_open)
    with pytest.raises(StorageError) as error:
        service.save_file(1, upload("one.jpg", "image/jpeg", b"one"))
    assert str(error.value) == "The storage operation failed."
