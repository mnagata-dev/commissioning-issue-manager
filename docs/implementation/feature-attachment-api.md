# Attachment API Integration Implementation Guide

## Purpose

Implement the Attachment HTTP API layer for the Commissioning Issue Manager (CIM).

This feature connects the existing Attachment / Storage foundation, Authentication API, Service, Repository, Model, and Schema implementations to the approved Attachment REST API contracts.

The implementation must remain documentation-first, minimal, and consistent with the existing layered architecture.

This file must be stored as:

```text
docs/implementation/feature-attachment-api.md
```

---

# Implementation Scope

Implement the following authenticated endpoints.

```http
POST /api/issues/{issue_id}/attachments
GET /api/issues/{issue_id}/attachments
GET /api/attachments/{attachment_id}
DELETE /api/issues/{issue_id}/attachments/{attachment_id}
```

The feature includes:

- Attachment API Router module
- FastAPI Dependency construction for `AttachmentService`
- Router registration
- Authentication integration using the existing `get_current_user` Dependency
- Attachment upload request handling using `multipart/form-data`
- Attachment list response construction
- Attachment download using a file response
- Attachment deletion response construction
- Minimal `AttachmentService` changes required by the approved list and download contracts
- Minimal `StorageService` changes required by the approved safe file-resolution contract
- Attachment API tests
- Focused Service and Storage tests
- Route registration and Dependency tests
- Relevant regression tests

Do not add `original_file_name` to the public `AttachmentResponse`.

---

# Source of Truth

Read the latest repository versions before changing code.

Follow the project document priority defined by `AGENTS.md`, `CONTRIBUTING.md`, and `project_conventions.md`.

At minimum, review:

- `docs/requirements/requirements.md`
- `docs/design/basic_design.md`
- `docs/design/database_design.md`
- `docs/design/api_design.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/project_conventions.md`
- `docs/adr/ADR-001-user-in-control.md`
- `docs/adr/ADR-002-target-type-definition.md`
- `docs/adr/ADR-003-category-definition.md`
- `docs/adr/ADR-004-room-model-design.md`
- `docs/adr/ADR-005-issue-as-aggregate-root.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- relevant existing files under `docs/implementation/`

Also inspect the current implementation before editing:

- `backend/app/api/deps.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/models/attachment.py`
- `backend/app/repositories/attachment_repository.py`
- `backend/app/repositories/issue_repository.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/schemas/attachment.py`
- `backend/app/services/attachment_service.py`
- `backend/app/services/storage_service.py`
- `backend/app/services/__init__.py`
- existing Attachment / Storage tests
- existing API and Dependency tests
- existing route-registration tests

If the current repository structure differs, follow the actual current structure and the latest Detailed Design. Do not create duplicate modules.

---

# Branch and Git Rules

Work only on:

```text
feature/attachment-api
```

Before editing, verify the current branch and working tree.

Do not:

- switch branches without instruction
- create another branch
- merge branches
- rewrite history
- force push
- commit
- push
- create a Pull Request
- modify unrelated files
- discard or overwrite existing user changes

Preserve all pre-existing modified and untracked files.

---

# Approved API Contract

## Upload Attachment

```http
POST /api/issues/{issue_id}/attachments
```

Request:

```text
Content-Type: multipart/form-data
```

Form field:

|Name|Type|Required|
|---|---|---|
|`file`|File|Yes|

Successful response:

```json
{
  "id": 1,
  "file_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "message": "Attachment uploaded"
}
```

Errors:

- `400` invalid file
- `401` unauthenticated
- `404` Issue not found
- common `500` behavior for unexpected storage or system failures

## Get Attachments

```http
GET /api/issues/{issue_id}/attachments
```

Successful response:

```json
{
  "items": [
    {
      "id": 1,
      "file_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
      "mime_type": "image/jpeg",
      "file_size": 204800,
      "uploaded_at": "2026-06-30T10:25:00"
    }
  ]
}
```

Errors:

- `401` unauthenticated
- `404` Issue not found

The public `AttachmentResponse` remains:

```python
id: int
file_name: str
mime_type: str
file_size: int
uploaded_at: datetime
```

Do not add `original_file_name`, `file_path`, or `uploaded_by`.

## Download Attachment

```http
GET /api/attachments/{attachment_id}
```

Return the physical file body.

Response behavior:

|Item|Approved value|
|---|---|
|`Content-Type`|Attachment metadata `mime_type`|
|Content disposition type|`inline`|
|Response filename|Attachment metadata `original_file_name`|

Use Starlette/FastAPI file-response support. Do not manually assemble a raw `Content-Disposition` header string.

Errors:

- `401` unauthenticated
- `404` Attachment metadata not found
- `404` physical file not found
- `500` invalid storage path or file-system failure

## Delete Attachment

```http
DELETE /api/issues/{issue_id}/attachments/{attachment_id}
```

Successful response:

```json
{
  "message": "Attachment deleted"
}
```

Errors:

- `401` unauthenticated
- `404` Issue not found
- `404` Attachment not found
- `404` Attachment does not belong to the specified Issue
- common `500` behavior for storage or system failures

---

# Architecture Rules

Preserve the existing layered architecture.

```text
HTTP Request
    │
    ▼
API Router
    │
    ▼
AttachmentService
    ├── AttachmentRepository
    ├── IssueRepository
    ├── UserRepository
    └── StorageService
```

## API Router Responsibilities

The Router may:

- receive path parameters
- receive the uploaded file
- receive the authenticated user through Dependency Injection
- call `AttachmentService`
- construct exact JSON responses
- convert approved Service download data to a file response
- declare response models

The Router must not:

- execute SQLAlchemy queries
- call Repository methods directly
- resolve Storage Root paths
- check physical file existence directly
- implement file validation
- implement Attachment/Issue ownership validation
- manage commit or rollback
- parse Session data manually
- expose `file_path`
- expose Storage Root details
- add undocumented response fields

## AttachmentService Responsibilities

Expected approved methods:

```python
upload_attachment(
    issue_id: int,
    file: UploadFile,
    user_id: int,
) -> UploadAttachmentResponse
```

```python
list_attachments(
    issue_id: int,
) -> list[AttachmentResponse]
```

```python
get_attachment_download(
    attachment_id: int,
) -> tuple[Path, str, str]
```

```python
delete_attachment(
    issue_id: int,
    attachment_id: int,
    user_id: int,
) -> None
```

The download tuple order is:

```python
(
    file_path,
    original_file_name,
    mime_type,
)
```

`list_attachments()` and `get_attachment_download()` are read operations and must not commit or rollback.

## StorageService Responsibilities

Add or reuse:

```python
resolve_file(
    file_path: str,
) -> Path | None
```

`resolve_file()` must:

- reject absolute paths
- prevent `..` traversal outside Storage Root
- prevent symlink escape outside Storage Root
- resolve only beneath Storage Root
- return only a regular file
- return `None` when the target does not exist
- avoid reading the whole file into memory
- convert invalid-path and filesystem failures to `StorageError`

It must not access SQLAlchemy, call Repositories, manage DB transactions, or generate HTTP responses.

## Repository Responsibilities

Repositories remain data-access-only.

Reuse existing methods such as:

```python
find_by_id(attachment_id: int)
list_by_issue(issue_id: int)
```

Do not add business validation, Storage access, HTTP logic, DTO construction, commit, or rollback.

---

# Authentication and Authorization

All four endpoints require the existing Cookie-based Session authentication.

Use:

```python
CurrentUserDependency
```

or the equivalent current alias.

Both `ADMINISTRATOR` and `ENGINEER` may use all Attachment endpoints.

|Endpoint|Authenticated User ID|
|---|---|
|Upload|Pass `current_user.id`|
|List|Do not add a Service user parameter|
|Download|Do not add a Service user parameter|
|Delete|Pass `current_user.id`|

Do not change Session configuration or add JWT/Bearer authentication.

---

# Service Dependency Construction

Add or extend the existing dependency module.

Expected dependency:

```python
get_attachment_service(...)
```

Expected alias:

```python
AttachmentServiceDependency
```

Construct `AttachmentService` using the request-scoped SQLAlchemy Session, existing Repositories required by its current constructor, and the existing `StorageService` construction pattern.

Do not perform database queries inside dependency functions.

---

# Router Integration

Expected module:

```text
backend/app/api/routes/attachments.py
```

Register the Router through:

- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`

Verify OpenAPI contains:

```text
/api/issues/{issue_id}/attachments
/api/attachments/{attachment_id}
```

with the approved HTTP methods.

---

# Upload Requirements

Reuse the existing Attachment / Storage foundation.

Do not redesign:

- allowed MIME types
- file-size limits
- generated file-name policy
- relative directory layout
- metadata fields
- transaction behavior
- compensation behavior
- Storage Root configuration

The Router must receive exactly one form field named `file`, use `UploadFile`, pass it unchanged to `upload_attachment()`, pass `current_user.id`, and return the existing `UploadAttachmentResponse`.

---

# List Requirements

Implement or reuse:

```python
list_attachments(issue_id: int) -> list[AttachmentResponse]
```

Required behavior:

1. verify Issue existence
2. call `AttachmentRepository.list_by_issue()`
3. preserve Repository ordering
4. convert each Attachment to `AttachmentResponse`
5. return no internal storage fields
6. perform no commit or rollback

The Router returns:

```json
{
  "items": [...]
}
```

Do not add pagination or a new public DTO unless already required by current project style.

---

# Download Requirements

Implement or reuse:

```python
get_attachment_download(
    attachment_id: int,
) -> tuple[Path, str, str]
```

Required behavior:

1. retrieve Attachment metadata through `AttachmentRepository.find_by_id()`
2. raise `NotFoundError` when metadata does not exist
3. pass Attachment `file_path` to `StorageService.resolve_file()`
4. raise `NotFoundError` when `resolve_file()` returns `None`
5. return resolved `Path`, `original_file_name`, and `mime_type`
6. perform no commit or rollback

The Router constructs a file response using:

```text
path = resolved file path
media_type = mime_type
filename = original_file_name
content_disposition_type = inline
```

Do not expose stored `file_name` as the response filename or read the file fully into memory.

---

# Delete Requirements

Reuse existing approved delete behavior.

The Router passes `issue_id`, `attachment_id`, and `current_user.id` to `delete_attachment()` and returns:

```json
{
  "message": "Attachment deleted"
}
```

Do not move transaction or storage-consistency behavior into the Router.

---

# Error Handling

Use existing project exceptions and common handlers.

|Condition|Behavior|HTTP|
|---|---|---|
|Invalid upload|`ValidationError`|400|
|Unauthenticated|`AuthenticationError`|401|
|Issue missing|`NotFoundError`|404|
|Attachment missing|`NotFoundError`|404|
|Physical file missing|`NotFoundError`|404|
|Attachment/Issue mismatch|`NotFoundError`|404|
|Invalid Storage path|`StorageError`|500|
|Filesystem failure|`StorageError`|500|

Do not expose filesystem paths, stack traces, SQLAlchemy details, or OS error details.

---

# Schema Policy

Reuse current schemas unchanged.

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

Do not add `original_file_name`, `file_path`, `uploaded_by`, or a download DTO.

---

# Explicitly Out of Scope

Do not implement:

- Frontend Attachment UI
- camera integration
- thumbnails
- image resizing
- video transcoding
- antivirus scanning
- cloud/object storage
- generic storage-provider abstractions
- background jobs
- Attachment update/edit
- Issue deletion
- Comment changes
- AI changes
- Authentication redesign
- authorization redesign
- JWT/Bearer/Refresh Tokens
- CORS or CSRF redesign
- database schema changes
- SQLAlchemy Model changes
- Alembic migrations
- public Attachment DTO changes
- unrelated dependency upgrades
- unrelated refactoring

---

# Dependency Policy

Prefer the standard library and existing FastAPI/Starlette functionality.

Do not add a storage framework, image/video package, MIME inspection package, cloud SDK, streaming package, or another DI framework.

If a runtime dependency appears necessary, stop before changing `pyproject.toml` or `uv.lock`.

---

# Documentation Policy

The user has already updated:

- `docs/design/api_design.md`
- `docs/design/detailed_design.md`
- `docs/implementation/feature-attachment-api.md`

Preserve these changes.

Do not modify Requirements, Design Documents, ADRs, Project Conventions, or this guide unless explicitly instructed.

If implementation reveals a documentation conflict, stop and report the exact conflicting files and sections.

---

# Tests

## Attachment API Tests

Cover:

- unauthenticated Upload/List/Download/Delete return `401`
- successful upload response
- authenticated User ID reaches upload Service
- exact multipart field `file`
- invalid upload returns common `400`
- Issue missing returns `404`
- successful list response
- empty list
- list exposes only approved fields
- successful file body
- `Content-Type` equals `mime_type`
- `Content-Disposition` is `inline`
- response filename uses `original_file_name`
- metadata missing returns `404`
- physical file missing returns `404`
- Storage failure returns common `500`
- successful delete response
- authenticated User ID reaches delete Service
- missing Issue/Attachment/mismatch return `404`

## AttachmentService Tests

Cover:

- list success and empty list
- Issue missing
- Repository order preserved
- DTO conversion
- download success tuple
- metadata missing
- physical file missing
- `resolve_file()` receives relative `file_path`
- list/download do not commit or rollback

## StorageService Tests

Cover:

- valid relative path returns `Path`
- missing target returns `None`
- absolute path rejected
- traversal rejected
- symlink escape rejected where supported
- directory target rejected
- valid target remains below Storage Root
- filesystem failure becomes `StorageError`
- file content is not loaded

Use temporary directories only.

## Dependency and Route Tests

Verify AttachmentService Dependency construction, no query in Dependency, expected methods and paths, preservation of existing routes, and no duplicate route.

Do not skip, xfail, weaken, or delete existing tests.

---

# Required Verification

Run focused tests from `backend/`:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q   tests/api/test_attachments.py   tests/services/test_attachment_service.py   tests/services/test_storage_service.py   tests/api/test_project_issue_dependencies.py   tests/test_main.py
```

Adjust only paths that differ in the actual repository.

Run the complete suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q
```

Also run:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
git diff --check
```

Report exact commands and results. Collection-only does not count as passing execution.

If the known TestClient/AnyIO `BlockingPortal` limitation appears, verify whether it is the same environment issue and run HTTP tests outside the normal sandbox when permitted.

---

# Stop Conditions

Stop before implementation or immediately when discovered if:

## Branch or Working Tree

- current branch is not `feature/attachment-api`
- user changes would need to be overwritten or discarded

## Design and Contract Ambiguity

- API Design and Detailed Design disagree
- public Attachment schemas conflict with the API contract
- download tuple order is ambiguous
- MIME type, filename, or disposition is ambiguous
- physical-file missing behavior is ambiguous
- `resolve_file()` behavior requires invention
- successful response shape or upload field name is unclear
- list ordering cannot be determined
- implementation requires adding `original_file_name` to `AttachmentResponse`

## Architecture Conflict

- Router would call a Repository
- Router would resolve Storage paths
- Dependency would query the database
- Repository would access filesystem
- StorageService would access SQLAlchemy
- AttachmentService would require HTTP objects
- a new layer/framework is required

## Existing-Code Conflict

- current constructors materially conflict with the design
- current StorageService cannot support `resolve_file()` without undocumented redesign
- existing routes conflict
- existing tests conflict with Source of Truth
- common error handling cannot represent approved behavior
- Attachment/Storage foundation requires redesign

## Scope Expansion

- Model or Migration changes are required
- new DB fields/relationships are required
- a new runtime dependency is required
- Authentication must change
- another API or Frontend change is required
- public DTO changes are required
- unrelated failures require unrelated code changes

When stopping, do not guess.

Report exact files/sections, conflict, why work cannot safely continue, minimum decision required, files already changed, and tests already run.

---

# Self-Review Requirements

Review the complete diff and confirm:

- all four endpoints implemented
- all use existing Session authentication
- Upload/Delete forward `current_user.id`
- Router calls Service only
- no SQLAlchemy query in Router or Dependency
- no Storage path resolution in Router
- Repository remains metadata-only
- StorageService remains filesystem-only
- AttachmentService owns validation and write transactions
- List/Download do not commit or rollback
- upload and delete responses are exact
- list contains approved fields only
- download uses metadata MIME type
- download uses `original_file_name`
- disposition is `inline`
- file is served without full memory loading
- missing physical file returns `404`
- invalid path/filesystem failure returns common `500`
- no public DTO, DB, Model, Migration, Frontend, dependency, or unrelated changes

---

# Completion Report

Use exactly these headings.

## Summary

Summarize the implemented Attachment API behavior.

## Modified Files

List all modified and new files. Separately identify pre-existing user changes preserved unchanged.

## Tests

For every command, report command, result, counts, collection-only results separately, environment, and limitations.

## Design Compliance

Confirm endpoint contracts, layer boundaries, Authentication, User ID forwarding, transaction ownership, safe path handling, download headers, no public DTO changes, and no DB/Migration changes.

## Assumptions

If none:

```text
None.
```

## Remaining Work

If none:

```text
None.
```

---

# Completion Criteria

Complete only when:

- all four endpoints are implemented
- all require Session authentication
- Upload accepts exact `file` field and returns approved response
- List returns approved fields only
- Download returns physical file with approved MIME type, original filename, and `inline`
- metadata/physical-file missing return `404`
- invalid paths/filesystem failures use common `500`
- Delete returns approved response
- Upload/Delete forward User ID
- Router has no business logic, queries, or path resolution
- `AttachmentService` list/download behavior is implemented
- `StorageService.resolve_file()` is safe
- read operations do not commit or rollback
- focused tests pass
- relevant regressions pass
- full suite runs or exact limitation is documented
- compile verification and `git diff --check` pass
- no Stop Condition remains unresolved
