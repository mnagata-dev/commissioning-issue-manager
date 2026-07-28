# Attachment / Storage Foundation Implementation Guide

## Feature

`feature/attachments-storage`

---

## Purpose

Implement the Attachment / Local Storage foundation for the Commissioning Issue Manager (CIM).

This feature establishes the application and storage behavior required to save and delete Issue attachment files while keeping Attachment metadata in SQLite consistent with Local Storage.

This file is the Codex implementation instruction for the feature and must be stored as:

```text
docs/implementation/feature-attachments-storage.md
```

---

## Read First

Before making changes, read the latest repository versions of:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/requirements/requirements.md`
- `docs/design/basic_design.md`
- `docs/design/database_design.md`
- `docs/design/api_design.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/project_conventions.md`
- `docs/adr/*`
- `docs/review_notes.md`
- `CHANGELOG.md`
- all existing files under `docs/implementation/`

Follow the source-of-truth priority defined in `AGENTS.md`.

Inspect the current implementation before editing, especially:

- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/models/attachment.py`
- `backend/app/models/issue.py`
- `backend/app/models/user.py`
- `backend/app/repositories/attachment_repository.py`
- `backend/app/repositories/issue_repository.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/schemas/attachment.py`
- `backend/app/services/`
- existing tests
- project dependency files

Do not assume an attached copy is newer than the repository version.

If the latest design documents or current implementation do not define enough information to implement Attachment / Storage behavior without guessing, apply the Stop Conditions below.

Do not modify design documents in this feature unless the user has already made and staged a design clarification before implementation begins.

---

# Current Design Contract

The current design establishes:

- Attachments belong to an Issue.
- Initial supported attachments are images and videos.
- Physical files are stored in Local Storage.
- Attachment metadata is stored in SQLite.
- Metadata includes `issue_id`, `file_name`, `original_file_name`, `file_path`, `mime_type`, `file_size`, `uploaded_by`, and `uploaded_at`.
- `file_path` is a relative storage path.
- `file_size` is stored in bytes and must be greater than zero.
- Attachment editing is not supported.
- `AttachmentRepository` owns metadata persistence only and must not delete physical files.
- `StorageService` owns physical file storage concerns.
- `AttachmentService` coordinates Issue validation, file validation, storage, metadata persistence, and deletion.
- Storage failures use `StorageError`.
- Invalid attachment input uses `ValidationError`.
- Failed operations must not leave an inconsistent partial state between SQLite metadata and Local Storage.

Conceptual Service methods:

```python
upload_attachment(
    issue_id: int,
    file: UploadFile,
    user_id: int,
) -> UploadAttachmentResponse

delete_attachment(
    issue_id: int,
    attachment_id: int,
    user_id: int,
) -> None
```

Conceptual Storage methods:

```python
save_file(
    issue_id: int,
    file: UploadFile,
) -> StoredFile

delete_file(
    file_path: str,
) -> None
```

Do not change these concepts unless the latest approved repository design explicitly differs.

---

# Scope

Implement only the Attachment / Storage foundation fully supported by the approved design.

Expected areas, once all required contracts are defined:

- `StorageService`
- internal `StoredFile` representation if required
- `AttachmentService`
- Local Storage configuration required by approved design
- service package exports where necessary
- focused Storage tests
- focused AttachmentService tests
- minimal configuration tests when storage configuration is added

Reuse the existing Attachment model, repositories, schemas, and exception classes.

---

# Out of Scope

Do not implement:

- Attachment API routes or Router registration
- HTTP download responses, `FileResponse`, or streaming
- Attachment list API
- authentication transport or FastAPI auth dependencies
- authorization dependencies
- Cookie, Session, JWT, or Token behavior
- frontend attachment UI or camera integration
- image processing, resizing, thumbnails
- video transcoding or media metadata extraction
- antivirus scanning
- cloud/object/remote storage
- background jobs or retry queues
- Attachment update/edit behavior
- Issue deletion
- database schema changes or Alembic migrations
- Attachment model redesign
- public Schema redesign
- AI changes
- unrelated refactoring

Do not create a generic storage-provider hierarchy for hypothetical future storage backends.

---

# Responsibility Boundary

## AttachmentService

Owns application-level Attachment behavior:

- verify Issue existence
- verify uploading User when required by current Service convention
- validate the attachment using approved rules
- call `StorageService` to save the physical file
- create Attachment metadata through `AttachmentRepository`
- coordinate transaction completion
- compensate for a saved file if metadata persistence fails
- verify Attachment existence before deletion
- verify Attachment belongs to the specified Issue
- coordinate physical-file and metadata deletion
- return the existing `UploadAttachmentResponse`

It must not:

- write files directly when `StorageService` owns storage
- execute direct SQLAlchemy queries
- generate HTTP responses
- know authentication transport
- perform undocumented authorization
- expose internal storage paths
- modify unrelated Issue fields
- implement download HTTP behavior

## StorageService

Owns Local Storage concerns only:

- generate storage-safe file names when defined
- generate relative storage paths when defined
- resolve paths beneath the configured storage root
- create required directories
- write uploaded bytes
- delete stored files
- return storage metadata required by `AttachmentService`
- convert storage I/O failures to `StorageError`

It must not access SQLAlchemy, repositories, database transactions, authorization, or API response logic.

All resolved physical paths must remain within the configured storage root. Never trust a client-supplied file name as a storage path. Absolute paths and path traversal must not escape the root.

---

# `StoredFile` Contract

The detailed design refers to `StoredFile` from `StorageService.save_file()`.

Before implementing it, confirm that the latest approved design or implementation defines its fields and ownership.

`AttachmentService` must ultimately obtain the metadata needed by the existing Attachment model:

- generated stored file name
- relative file path
- MIME type if StorageService owns its determination
- file size

The original client file name is stored separately.

Do not invent a public DTO for `StoredFile`. If its exact internal contract is not defined, stop and report it.

---

# Storage Configuration

Inspect `app/core/config.py` and the latest design for approved Local Storage configuration.

The implementation requires an unambiguous storage root/base directory. The database stores a relative `file_path`, never a machine-specific absolute path.

Do not hard-code a developer-specific Windows, WSL, or Linux path.

If these are undefined, stop and report them:

- storage root setting
- environment variable name, if environment-driven
- default storage root, if required
- relative directory layout beneath the root

Tests must use a temporary directory and never real application storage.

---

# File Name and Path Policy

Before implementation, confirm the approved design defines:

- generated file-name format
- whether the original extension is preserved
- collision-avoidance strategy
- Issue-specific directory layout
- normalization/sanitization rules
- behavior for missing or invalid original file names

Do not use the original file name directly as the physical storage file name unless explicitly approved.

Do not invent UUID, timestamp, sequence, hash, or random-name conventions.

If these rules are undefined, stop and report them.

---

# File Type Validation

The design permits images and videos, but implementation requires the exact contract.

Confirm:

- exact accepted image types
- exact accepted video types
- whether validation uses MIME type, extension, both, or file content/signature

Do not treat arbitrary `image/*` or `video/*` as allowed unless explicitly approved.

Do not add media-inspection dependencies merely to infer policy.

If exact accepted types or validation rules are undefined, stop and report them.

---

# File Size Validation

Confirm:

- maximum allowed file size
- whether images and videos have the same or different limits
- zero-byte-file behavior
- how size is determined

Do not invent a maximum size or silently truncate files.

If the limit is undefined, stop and report it.

---

# Upload Behavior

Expected conceptual flow:

```text
validate Issue
    ↓
validate User if required
    ↓
validate file
    ↓
save physical file
    ↓
create Attachment metadata
    ↓
commit database transaction
    ↓
return UploadAttachmentResponse
```

Use the existing model fields and UTC timestamp policy.

Do not return `file_path`, `original_file_name`, `uploaded_by`, or binary content in the public response.

---

# Upload Consistency and Transaction Behavior

Required behavior:

- Storage save failure must not persist metadata.
- Metadata registration or DB transaction failure after file save must remove the saved physical file.
- Failed upload must not be reported as successful.
- Repositories do not own transaction completion.

Before implementing compensation, confirm behavior when:

1. file save succeeds,
2. metadata persistence fails,
3. compensating file deletion also fails.

Do not invent a recovery queue or hide this failure. If undefined, stop and report it.

---

# Delete Behavior

Expected conceptual checks:

```text
validate Issue
    ↓
find Attachment
    ↓
validate Attachment belongs to Issue
    ↓
delete physical file
    ↓
delete Attachment metadata
    ↓
commit database transaction
```

Required behavior includes:

- physical file deletion
- metadata deletion
- missing Issue rejection
- missing/already-deleted Attachment rejection
- Attachment/Issue mismatch rejection
- storage delete failure must not complete metadata deletion
- no partial state

Before implementation, confirm what happens if the physical file is deleted successfully but metadata deletion or DB commit then fails.

A DB rollback cannot restore a deleted file. Do not invent backup/restore, tombstones, staging, or recovery queues. If the strategy is undefined, stop and report it.

Also confirm deletion behavior when metadata exists but the physical file is already missing.

---

# Exceptions

Reuse existing application exceptions.

Expected categories:

- `ValidationError` for invalid attachment input
- `NotFoundError` for missing resources where defined
- `StorageError` for physical storage failures

Do not expose absolute paths, OS exception details, storage root, or stack traces.

Do not add a new exception unless approved.

If `StorageError` construction or public behavior is ambiguous, stop and report it.

---

# Repository Rules

Use existing repository methods conceptually:

```python
AttachmentRepository.find_by_id(attachment_id)
AttachmentRepository.list_by_issue(issue_id)
AttachmentRepository.create(attachment)
AttachmentRepository.delete(attachment)
```

Repository remains metadata-only.

Do not:

- make Repository write/delete physical files
- call `StorageService` from Repository
- commit from Repository
- bypass Repository with direct SQLAlchemy queries in `AttachmentService`

Reuse existing Issue/User repositories rather than duplicating queries.

---

# Schema Rules

Reuse existing Attachment schemas.

Conceptual public contracts:

```python
AttachmentResponse(
    id: int,
    file_name: str,
    mime_type: str,
    file_size: int,
    uploaded_at: datetime,
)
```

```python
UploadAttachmentResponse(
    id: int,
    file_name: str,
    message: str,
)
```

Do not expose internal storage information or change these schemas merely to simplify implementation.

---

# Dependencies

Prefer the Python standard library and existing FastAPI/Starlette types.

Do not add a storage framework, MIME/media inspection package, image/video library, or cloud-storage package unless explicitly approved.

Do not introduce unrelated tooling or dependency upgrades.

---

# Tests

## Storage Tests

Use a test-only temporary directory.

Cover, once contracts are defined:

- image save
- video save
- approved generated file-name policy
- approved relative-path policy
- directory creation
- correct file size
- content preservation
- deletion
- unrelated files not deleted
- storage I/O failure -> `StorageError`
- path traversal cannot escape root
- absolute client names cannot escape root
- test storage isolation

## AttachmentService Tests

Cover at minimum:

### Upload

- successful image/video upload
- existing response fields
- Issue not found
- User not found when required
- invalid file type
- invalid file name
- zero-byte file
- oversized file
- correct metadata
- UTC `uploaded_at`
- successful commit once
- validation failure saves nothing
- storage save failure creates no metadata
- metadata creation failure rolls back and removes saved file
- DB commit failure follows approved compensation
- no successful partial state

### Delete

- successful deletion
- Issue not found
- Attachment not found/already deleted
- Attachment/Issue mismatch
- storage delete failure prevents completed metadata deletion
- successful metadata deletion and one commit
- failure rolls back DB transaction
- metadata failure after physical deletion follows approved strategy
- missing physical file follows approved design

Do not invent expectations for undefined behavior.

---

# Existing Tests

Do not weaken, delete, skip, or rewrite existing tests merely to make this feature pass.

Keep Repository tests authoritative for metadata persistence and Schema tests authoritative for public DTO shape.

If an unrelated existing test fails, report it rather than changing unrelated code.

---

# Required Verification

Run focused tests from `backend/`:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest <focused attachment/storage test paths>
```

Run relevant regression tests, then:

```bash
git diff --check
```

Attempt:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

If the known unrelated `tests/test_main.py::test_application_error_uses_common_response` timeout remains, report it accurately and do not change unrelated code.

Report exact commands and results.

---

# Design Compliance

Preserve these boundaries:

- physical files in Local Storage
- metadata in SQLite
- DB `file_path` is relative
- Attachment subordinate to Issue
- Repository metadata-only
- StorageService filesystem-only
- AttachmentService coordinates application behavior
- no API Router
- no authentication transport
- no DB schema/migration changes
- no public Attachment DTO changes
- no unrelated refactoring

---

# Git Rules

Work only on the feature branch prepared by the user.

Before editing, verify the current branch.

Do not create/switch branches unless requested. Do not commit, push, merge, amend, reset, discard user changes, or modify unrelated files.

Preserve user-authored and already-staged design changes.

---

# Completion Report

When complete, report:

## Summary

Attachment / Storage components implemented and tests added.

## Modified Files

List every modified/new file and distinguish pre-existing user changes.

## Storage Behavior

Summarize storage root/configuration, directory layout, file-name policy, relative-path policy, save/delete behavior, and path safety.

## AttachmentService Methods

List implemented public methods.

## Validation Behavior

Summarize Issue/User/file-type/file-name/file-size/ownership validation.

## Transaction and Consistency Behavior

Confirm successful commit behavior, rollback behavior, compensation, storage failures, metadata failures, Repository transaction boundaries, and absence of direct SQLAlchemy queries in Services.

## Tests

Report each command and exact result.

## Design Compliance

Confirm no API routes, auth transport, DB/model/migration changes, public Schema changes, Repository storage behavior, cloud storage, or unrelated refactoring.

## Issues or Ambiguities

List unresolved issues; if none, say none remain.

## Remaining Work

- Attachment API integration
- Attachment list/download HTTP behavior
- API authentication integration
- remaining API Layer
- Frontend integration
- real-environment upload/download verification

---

# Stop Conditions

Stop and report before continuing if any of these is found:

- Local Storage root/base-directory configuration is undefined.
- Storage environment-variable name/default is undefined when required.
- Relative directory layout is undefined.
- Generated storage file-name policy is undefined.
- Collision handling is undefined.
- Exact allowed image/video file types are undefined.
- MIME/extension/content validation ownership is undefined.
- Maximum allowed file size is undefined.
- Image/video size-limit relationship is ambiguous.
- `StoredFile` contract is insufficiently defined.
- Original-file-name/invalid-file-name handling is ambiguous.
- `StorageError` construction/public behavior is ambiguous.
- User existence validation conflicts with current Service convention/design.
- Upload compensation behavior is undefined when cleanup also fails.
- Delete consistency is undefined when physical deletion succeeds but metadata/commit fails.
- Missing physical-file deletion behavior is undefined.
- Existing repositories cannot support approved behavior.
- Implementation would require direct SQLAlchemy queries in `AttachmentService`.
- Implementation requires Attachment model/migration changes.
- Implementation requires public Attachment DTO changes.
- Implementation requires Attachment API/HTTP behavior.
- An unrelated test failure would require changes outside this feature.
- Latest design documents conflict on a required Attachment/Storage rule.

Do not resolve storage paths, file names, MIME rules, size limits, transaction compensation, or deletion consistency by guessing.
