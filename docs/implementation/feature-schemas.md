# Schema Layer Implementation Guide

## Feature

`feature/schemas`

---

## Purpose

Implement the Pydantic DTOs defined for the Commissioning Issue Manager (CIM).

This feature establishes the Request and Response Schema layer required by the Service Layer and later API implementation.

This file is the Codex implementation instruction for the feature and must be stored as:

```text
docs/implementation/feature-schemas.md
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
- `docs/implementation/feature-backend-foundation.md`
- `docs/implementation/feature-database-models.md`
- `docs/implementation/feature-repositories.md`

Follow the source-of-truth priority defined in `AGENTS.md`.

Inspect the current code before editing. Do not assume an attached copy is newer than the repository version.

If the latest design documents conflict with each other or with the installed Pydantic version, do not guess. Report the inconsistency and stop only the affected work.

Do not modify design documents in this feature.

---

## Scope

Implement the DTOs currently defined in the detailed design:

### Authentication

- `LoginRequest`
- `CurrentUserResponse`

### Project

- `ProjectResponse`
- `ProjectListResponse`

### Issue

- `CreateIssueRequest`
- `UpdateIssueRequest`
- `UpdateIssueStatusRequest`
- `IssueSummaryResponse`
- `IssueDetailResponse`

### AI Draft

- `GenerateDraftRequest`
- `GenerateDraftResponse`

### Comment

- `CreateCommentRequest`
- `CommentResponse`

### Attachment

- `AttachmentResponse`
- `UploadAttachmentResponse`

Add only the small nested Response DTOs required to replace the design's untyped `dict` fields with the exact structures shown in the API examples:

- `HotelReferenceResponse`
- `ProjectReferenceResponse`
- `RoomReferenceResponse`
- `UserReferenceResponse`

These nested DTOs are structural types only. They must not contain business logic.

Also implement:

- Schema package exports
- Focused Schema tests

---

## Out of Scope

Do not implement or modify:

- Services
- Repositories
- API routes
- Authentication logic
- Password hashing or verification
- Token or session handling
- AI integration
- File upload handling
- File storage
- Database models
- Database schema
- Alembic migrations
- Exception classes
- Frontend
- Unrelated refactoring

Do not add DTOs that are not required by the current detailed design or API examples.

Do not introduce generic base DTO classes unless an existing project convention already requires one.

---

## Expected Directory Structure

Use the existing project structure. Prefer:

```text
backend/
├── app/
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py
│       ├── common.py
│       ├── project.py
│       ├── issue.py
│       ├── ai.py
│       ├── comment.py
│       └── attachment.py
└── tests/
    └── schemas/
        ├── __init__.py
        ├── test_auth_schemas.py
        ├── test_project_schemas.py
        ├── test_issue_schemas.py
        ├── test_ai_schemas.py
        ├── test_comment_schemas.py
        └── test_attachment_schemas.py
```

`common.py` is for the four nested reference DTOs only.

If the repository already establishes a different Schema module naming convention, follow that convention instead.

Do not create empty placeholder modules.

---

# General Schema Rules

All DTOs must:

- Inherit from Pydantic `BaseModel`.
- Use the Pydantic version already installed by the project.
- Use Python type hints.
- Match the field names and required/optional status in the latest detailed design.
- Preserve API-facing string values such as Status, Category, Target Type, and Role.
- Use `datetime` for timestamp fields.
- Use typed nested DTOs instead of raw `dict` for the exact structures defined below.
- Reject undeclared extra fields unless the current project convention explicitly allows them.
- Remain free of database access and business logic.

Do not:

- Import SQLAlchemy `Session`.
- Query repositories.
- Commit or roll back transactions.
- Raise application-layer custom exceptions.
- Use FastAPI `HTTPException`.
- Depend on API Router modules.
- Add cross-field business validation.
- Duplicate Service validation.
- Convert API strings to database-specific representations.
- Add aliases that are not defined by the API design.
- Add serialization behavior that changes the documented JSON field names.

---

## Validation Boundary

The Schema layer owns only structural input validation:

- Required fields
- Optional fields
- Basic Python/Pydantic type validation
- Nested response structure
- Rejection of undeclared fields

The Service layer owns business validation, including:

- Allowed Target Type values
- Allowed Category values
- Allowed Status values
- `ROOM` and `OTHER` consistency
- Whether `room_id` is required or forbidden
- Whether `target` is required or forbidden
- Project, Room, User, and Issue existence
- Room/Project Hotel matching
- Empty or whitespace-only Description
- Empty or whitespace-only Comment
- Status transition rules, if defined later

Therefore:

- Keep `target_type`, `category`, `status`, and `role` as `str`.
- Do not add Pydantic cross-field validators for Target rules.
- Do not strip or normalize input text in Schemas.
- Do not reject empty strings through custom validators in this feature.
- Do not use database Enum classes as API field types.

This boundary is required so Service behavior remains explicit and testable.

---

## Extra Fields

Configure DTOs to reject undeclared input fields.

Use the Pydantic configuration style supported by the installed version.

Do not create a custom base model solely to share this one setting unless the project already has such a convention. Repeating a small model configuration is acceptable when it keeps the implementation explicit.

---

## ORM Conversion

Do not enable ORM/entity conversion globally without a current requirement.

The DTOs are API boundary objects. The Service Layer is expected to construct response DTOs explicitly.

If an existing project convention already uses Pydantic's attribute-based validation, follow it consistently and document that choice in the Completion Report.

Do not add compatibility code for multiple Pydantic major versions.

---

# Common Nested Response DTOs

Implement these exact structures.

## `HotelReferenceResponse`

```python
id: int
name: str
```

Used by `ProjectResponse.hotel`.

## `ProjectReferenceResponse`

```python
id: int
name: str
```

Used by `IssueDetailResponse.project`.

## `RoomReferenceResponse`

```python
id: int
room_number: str
```

Used by Issue response DTOs.

## `UserReferenceResponse`

```python
id: int
display_name: str
```

Used by `IssueDetailResponse` and `CommentResponse`.

Do not add unrelated fields such as username, role, hotel_id, or timestamps.

---

# Authentication DTOs

## `LoginRequest`

```python
username: str
password: str
```

Both fields are required.

Do not implement password validation or authentication logic.

## `CurrentUserResponse`

```python
id: int
username: str
display_name: str
role: str
```

Do not use the database Role enum as the DTO field type.

---

# Project DTOs

## `ProjectResponse`

```python
id: int
name: str
hotel: HotelReferenceResponse
```

## `ProjectListResponse`

```python
projects: list[ProjectResponse]
```

Do not add pagination because the current Project API design does not define it.

---

# Issue Request DTOs

## `CreateIssueRequest`

```python
room_id: int | None
target_type: str
target: str | None
category: str
description: str
```

Required/optional behavior:

- `room_id` is optional and defaults to `None`.
- `target_type` is required.
- `target` is optional and defaults to `None`.
- `category` is required.
- `description` is required.

Do not add `project_id`, `status`, `created_by`, or timestamps.

Do not validate `ROOM`/`OTHER` combinations here.

## `UpdateIssueRequest`

```python
room_id: int | None
target_type: str
target: str | None
category: str
description: str
```

This DTO represents the current `PUT` API, not a partial `PATCH`.

Required/optional behavior:

- `room_id` accepts `None` but the field itself is required.
- `target_type` is required.
- `target` accepts `None` but the field itself is required.
- `category` is required.
- `description` is required.

Do not make all fields optional.

Do not add `status`; Status has a separate request DTO.

Do not add `raw_input_text`, because it is not part of the current Update design.

## `UpdateIssueStatusRequest`

```python
status: str
```

Do not restrict the value with a Schema enum. Service validation owns allowed Status values.

---

# Issue Response DTOs

## `IssueSummaryResponse`

```python
id: int
room: RoomReferenceResponse | None
target_type: str
target: str | None
category: str
description: str
status: str
updated_at: datetime
```

## `IssueDetailResponse`

```python
id: int
project: ProjectReferenceResponse
room: RoomReferenceResponse | None
target_type: str
target: str | None
category: str
description: str
status: str
created_by: UserReferenceResponse
updated_by: UserReferenceResponse
created_at: datetime
updated_at: datetime
comments: list[CommentResponse]
attachments: list[AttachmentResponse]
```

The API example includes `updated_by`; include it even if an older DTO snippet omits it.

This resolves the detailed-design/API-example mismatch in favor of the API's explicit response contract.

Use forward imports or module organization that avoids circular imports cleanly.

Do not use `dict` or `Any` for the nested fields.

Do not add list pagination fields to `IssueSummaryResponse`. Pagination wrapping belongs to the later API layer unless a named DTO is added to the design.

---

# AI DTOs

## `GenerateDraftRequest`

```python
project_id: int
target_type: str
room_id: int | None
target: str | None
input_text: str
```

Required/optional behavior:

- `project_id` is required.
- `target_type` is required.
- `room_id` accepts `None` and defaults to `None`.
- `target` accepts `None` and defaults to `None`.
- `input_text` is required.

Do not implement Target consistency or AI prompt validation.

## `GenerateDraftResponse`

```python
category: str
description: str
```

---

# Comment DTOs

## `CreateCommentRequest`

```python
comment: str
```

Do not add Issue or User IDs; they come from the route and authenticated user context.

## `CommentResponse`

```python
id: int
comment: str
created_by: UserReferenceResponse
created_at: datetime
```

---

# Attachment DTOs

## `AttachmentResponse`

```python
id: int
file_name: str
mime_type: str
file_size: int
uploaded_at: datetime
```

Do not include internal storage paths, original file names, uploader IDs, or Issue IDs.

## `UploadAttachmentResponse`

Use the API response contract:

```python
id: int
file_name: str
message: str
```

The API example includes `file_name`; include it even if an older DTO snippet omits it.

Do not include the uploaded binary or internal storage path.

---

# Package Exports

Update `app/schemas/__init__.py` to export every public DTO implemented by this feature.

Use one module docstring.

Export:

- `LoginRequest`
- `CurrentUserResponse`
- `HotelReferenceResponse`
- `ProjectReferenceResponse`
- `RoomReferenceResponse`
- `UserReferenceResponse`
- `ProjectResponse`
- `ProjectListResponse`
- `CreateIssueRequest`
- `UpdateIssueRequest`
- `UpdateIssueStatusRequest`
- `IssueSummaryResponse`
- `IssueDetailResponse`
- `GenerateDraftRequest`
- `GenerateDraftResponse`
- `CreateCommentRequest`
- `CommentResponse`
- `AttachmentResponse`
- `UploadAttachmentResponse`

Do not export private helpers.

Keep `__all__` deterministic and readable.

---

# Tests

## Test Strategy

Use focused unit tests for Pydantic DTO behavior.

Do not use a database, SQLAlchemy Session, Repository, Service, FastAPI TestClient, or file system.

Tests must use the installed Pydantic API directly.

Verify DTO construction and serialization without testing Pydantic itself exhaustively.

---

## Authentication Tests

Cover:

- Valid `LoginRequest`
- Required username
- Required password
- Extra fields rejected
- Valid `CurrentUserResponse`

Do not test password strength.

---

## Project Tests

Cover:

- Valid nested `ProjectResponse`
- Valid `ProjectListResponse`
- Hotel structure is typed and serialized correctly
- Missing required nested fields rejected
- Extra fields rejected

---

## Issue Request Tests

Cover:

- Valid ROOM-shaped `CreateIssueRequest`
- Valid OTHER-shaped `CreateIssueRequest`
- Optional room_id and target default to None.
- Required Create fields
- Extra fields rejected
- Valid `UpdateIssueRequest`
- `room_id=None` and `target=None` are accepted when explicitly provided
- Update fields are required because the API uses `PUT`
- Valid `UpdateIssueStatusRequest`

Do not test Target combinations as invalid in Schema tests. Those are Service rules.

Do not reject arbitrary Category, Status, or Target Type strings in Schema tests.

---

## Issue Response Tests

Cover:

- Valid `IssueSummaryResponse` with Room
- Valid `IssueSummaryResponse` without Room
- Valid complete `IssueDetailResponse`
- `updated_by` is present
- Comments and Attachments serialize as typed lists
- `datetime` fields serialize through Pydantic's normal JSON serialization
- Invalid nested response structures are rejected
- Extra fields rejected

---

## AI Tests

Cover:

- Valid `GenerateDraftRequest`
- Optional `room_id` and `target`
- Required fields
- Valid `GenerateDraftResponse`
- Extra fields rejected

Do not test AI behavior.

---

## Comment Tests

Cover:

- Valid `CreateCommentRequest`
- Required Comment field
- Valid typed `CommentResponse`
- Extra fields rejected

Do not reject an empty string at Schema level.

---

## Attachment Tests

Cover:

- Valid `AttachmentResponse`
- Valid `UploadAttachmentResponse`
- `file_name` is required in `UploadAttachmentResponse`
- Required fields
- Extra fields rejected

Do not test file validation or storage behavior.

---

# Required Verification

Run from `backend/`:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/schemas
```

Then run:

```bash
git diff --check
```

Then attempt the full test suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

If the full suite encounters the already known timeout in `test_application_error_uses_common_response`:

- Report the timeout accurately.
- Confirm whether the new Schema tests passed independently.
- Do not modify the unrelated API exception-handler test.
- Do not claim the full suite passed.

Run an existing configured linter or formatter only when it is already available in project dependencies or documented commands.

Do not add a dependency solely for formatting.

---

# Completion Report

When implementation is complete, report:

## Summary

- DTO modules implemented
- DTO classes implemented
- Tests added

## Modified Files

List every modified and new file.

## Schema Classes

List all public DTOs by module.

## Validation Boundary

Confirm:

- Structural validation is implemented.
- Extra fields are rejected.
- Business and cross-field validation is not implemented in Schemas.
- API enum-like values remain `str`.
- Database enum classes are not used by Schemas.

## Serialization Behavior

Confirm:

- Nested DTOs are typed.
- Datetimes use Pydantic serialization.
- Internal database and storage fields are not exposed.

## Tests

Report each command and its exact result.

## Design Compliance

Confirm:

- No Service, Repository, API, Model, Migration, Authentication, AI, Storage, or Frontend implementation was added.
- No database access exists in Schemas.
- No unrelated refactoring was performed.

## Issues or Ambiguities

List unresolved issues. If none remain, state that none remain.

## Remaining Work

State that Service Layer and API implementation remain after this feature.

---

# Stop Conditions

Stop and report before continuing if:

- The installed Pydantic major version cannot support the required DTO design.
- Current design documents define contradictory field names or required/optional behavior not explicitly resolved by this guide.
- A DTO requires a field whose API structure is not defined.
- Existing code already defines conflicting DTO classes.
- Implementing a DTO requires changing a database model or migration.
- Implementing a DTO requires adding business logic or database access.
- Circular imports cannot be resolved through normal module organization.
- Existing project conventions require a materially different Schema structure.
- An unrelated test failure would require changing code outside this feature.

Do not resolve new design ambiguity by guessing.
