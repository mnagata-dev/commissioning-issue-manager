# Service Layer Implementation Guide

## Feature

`feature/services`

---

## Purpose

Implement the core Service Layer for the Commissioning Issue Manager (CIM).

This feature adds application-level business logic between the API Router and Repository Layer. Services must validate business rules, coordinate repositories, and control transaction completion.

This implementation guide is also the Codex implementation instruction for this feature.

---

## Read First

Before making changes, read the latest versions of:

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

Always inspect the current implementation before editing. Do not assume that an uploaded copy of a design document is newer than the repository version.

If the current documents, existing models, repositories, schemas, or exception classes conflict, do not guess or silently change the design. Report the inconsistency and stop only the affected work until it is clarified.

Do not modify design documents in this feature.

---

## Scope

Implement only the core services that can be completed using the existing domain models and repositories:

- `ProjectService`
- `IssueService`
- `CommentService`
- Service package initialization where necessary
- Unit tests for these services
- Minimal service-specific test fixtures or test helpers

The following services are explicitly out of scope for this feature:

- `AuthService`
- `AIService`
- `AttachmentService`
- `StorageService`

They require separate security, AI-client, upload-validation, or file-storage decisions and will be implemented in later features.

Also out of scope:

- API routes
- Authentication dependencies
- Password hashing or verification
- Token or session handling
- Ollama integration
- File upload or file-system operations
- Attachment metadata operations
- Pydantic schema redesign
- Repository changes unless a proven defect prevents the Service implementation
- Database schema changes
- Alembic migrations
- Frontend work
- Unrelated refactoring

Do not add undocumented Service classes or generic base Service classes.

---

## Expected Directory Structure

Follow the existing project structure. Use the following structure unless the repository already establishes an equivalent convention:

```text
backend/
├── app/
│   └── services/
│       ├── __init__.py
│       ├── project_service.py
│       ├── issue_service.py
│       └── comment_service.py
└── tests/
    └── services/
        ├── __init__.py
        ├── conftest.py
        ├── test_project_service.py
        ├── test_issue_service.py
        └── test_comment_service.py
```

Do not move or rename existing files unnecessarily.

---

## General Service Rules

Each Service must:

- Receive required repositories and the SQLAlchemy `Session` through constructor injection.
- Use existing repositories for data access.
- Own business validation.
- Own transaction completion.
- Call `session.commit()` once after a successful write operation.
- Call `session.rollback()` when an exception occurs during a write operation.
- Re-raise the original application exception after rollback.
- Let unexpected exceptions propagate after rollback.
- Use existing custom application exceptions.
- Use domain entities and existing enums.
- Use type hints.
- Follow the existing synchronous implementation style.

Services must not:

- Execute SQLAlchemy queries directly.
- Call `session.add()`, `session.delete()`, or `session.flush()` directly.
- Create their own database sessions.
- Raise FastAPI `HTTPException`.
- Depend on API Router classes.
- Perform HTTP response formatting.
- Perform authorization rules not yet defined by the current design.
- Duplicate Repository query logic.
- Commit read-only operations.
- Add logging infrastructure unless already established by the project.
- Catch exceptions only to suppress them.
- Modify database models, repositories, migrations, or schemas without reporting the blocking inconsistency first.

Example constructor pattern:

```python
class IssueService:
    def __init__(
        self,
        session: Session,
        project_repository: ProjectRepository,
        room_repository: RoomRepository,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        comment_repository: CommentRepository,
        attachment_repository: AttachmentRepository,
    ) -> None:
        self.session = session
        self.project_repository = project_repository
        self.room_repository = room_repository
        self.issue_repository = issue_repository
        self.user_repository = user_repository
        self.comment_repository = comment_repository
        self.attachment_repository = attachment_repository
```

Use only the dependencies actually required by each Service. Do not inject unused repositories.

---

## DTO and Entity Boundary

Use the request and response schema classes already present in the repository when they match the latest design.

Do not redesign schemas in this feature.

If required schema classes are not yet implemented, or their fields conflict with the current design:

1. Do not invent alternate DTOs.
2. Do not silently change method signatures.
3. Report the missing or conflicting schema classes.
4. Stop the affected Service implementation until the schema boundary is clarified.

Do not return SQLAlchemy entities directly from API routes. This feature does not implement API routes.

Where the detailed design explicitly says that the API Router constructs the final response, a Service may return domain entities or simple application values only when that behavior is already established by the current code and schemas. Do not guess between entity and DTO return styles when the repository has no established convention.

---

## Exception Rules

Use the existing custom exceptions from `app.core.exceptions`.

Expected exception types include:

- `ValidationError`
- `NotFoundError`
- `BusinessRuleError`

Do not add duplicate exception classes.

Use `NotFoundError` when a requested database entity does not exist.

Use `ValidationError` for invalid values or invalid combinations supplied by the caller.

Use `BusinessRuleError` only for a documented business-state conflict that is not simply malformed input.

Do not expose internal exception details in messages.

Use stable, concise messages that identify the invalid resource or rule. Follow existing exception constructor conventions exactly.

If existing exception constructors or required error codes are unclear, inspect current tests and exception handlers. If still ambiguous, report the ambiguity and stop the affected implementation.

---

## Transaction Policy

Read-only methods:

- Must not call `commit()`.
- Must not call `rollback()` unless they catch and re-raise an exception for an established reason.
- Must not mutate entities.

Write methods:

```python
try:
    # validate
    # modify or construct entity
    # call repository create/update
    session.commit()
except Exception:
    session.rollback()
    raise
```

Additional requirements:

- Perform all business validation before committing.
- Do not commit partially completed work.
- Call `commit()` only after all Repository operations succeed.
- Do not call `flush()` from the Service when the Repository already owns write synchronization.
- Do not call `refresh()` unless the current design or existing implementation requires it.
- Do not perform a second commit in the same Service method.

---

## Timestamp Policy

Follow the current timestamp policy defined by the design and model implementation:

- Timestamps are UTC.
- SQLite stores timezone-naive UTC values.
- Application code generates timestamps in Python.
- Use the existing shared clock or timestamp utility if one already exists.
- Otherwise follow the established model/service convention in the repository.

Do not introduce a new time library or time abstraction solely for this feature.

Tests must use deterministic timestamps. Do not make assertions that depend on the real current second unless the existing test convention already supports that safely.

---

# ProjectService

## Responsibilities

- Retrieve the Project list.
- Validate that a Project exists.

## Dependencies

Use only:

- `ProjectRepository`

Inject `Session` only if required by the established Service constructor convention. `ProjectService` has no write transaction and must not commit.

## Methods

Implement the signatures defined by the current detailed design and schemas.

Expected conceptual operations:

```python
list_projects(user_id: int)

validate_project_exists(project_id: int) -> None
```

### `list_projects()`

Requirements:

- Retrieve Projects through `ProjectRepository.list_all()`.
- Preserve the Repository order.
- Include related Hotel information through the data already loaded by the Repository.
- Do not query Hotel separately.
- Do not implement user-specific Project filtering unless a current design document explicitly defines it and the current data model supports it.
- Do not implement authorization in this feature.
- Do not commit.

The `user_id` parameter must not trigger invented access-control behavior. If the current schema or design requires user-specific Project access but no relationship exists, report the inconsistency.

### `validate_project_exists()`

Requirements:

- Call `ProjectRepository.find_by_id(project_id)`.
- Raise `NotFoundError` when no Project exists.
- Return `None` when the Project exists.
- Do not commit.

Do not add a separate `HotelRepository`.

---

# IssueService

## Responsibilities

- List Issues.
- Get Issue detail.
- Create Issue.
- Update Issue.
- Update Issue Status.
- Validate Project existence.
- Validate User existence where a creator or updater is required.
- Validate Room existence.
- Validate that the Room belongs to the Project's Hotel.
- Validate Target Type and Room/Target consistency.
- Validate Category.
- Validate Status.
- Validate non-empty Description.

## Dependencies

Use only the repositories required by the implemented methods:

- `ProjectRepository`
- `RoomRepository`
- `IssueRepository`
- `UserRepository`
- `CommentRepository`
- `AttachmentRepository`

Use `CommentRepository` and `AttachmentRepository` only if the current `IssueDetailResponse` construction belongs in the Service according to the existing schema and implementation convention.

Do not add direct SQLAlchemy queries.

## Methods

Implement the signatures defined by the current detailed design and schemas.

Expected conceptual operations:

```python
list_issues(
    project_id: int,
    status: str | None,
    category: str | None,
    target_type: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
)

get_issue_detail(issue_id: int)

create_issue(
    project_id: int,
    request: CreateIssueRequest,
    user_id: int,
) -> int

update_issue(
    issue_id: int,
    request: UpdateIssueRequest,
    user_id: int,
) -> None

update_status(
    issue_id: int,
    request: UpdateIssueStatusRequest,
    user_id: int,
) -> None
```

Do not alter these conceptual responsibilities to work around missing schemas. Apply the DTO stop rule when necessary.

---

## Issue List

### Validation

- Verify that the Project exists before returning its Issue list.
- Require `page >= 1`.
- Require `page_size >= 1`.
- Do not define a maximum `page_size` or default values in this feature.
- Query parameter defaults and maximum limits belong to the later API Layer unless explicitly added to the design.
- Validate filter enum values only when they are not `None`.
- Do not normalize invalid enum values silently.
- Do not trim or transform keyword values unless the current schema already defines that behavior.

### Pagination

Convert page-based input to Repository offset/limit:

```text
offset = (page - 1) * page_size
limit = page_size
```

Because `page >= 1` and `page_size >= 1` are required, do not pass negative offsets or non-positive limits.

Use:

- `IssueRepository.list_by_project(...)`

Do not call `IssueRepository.count_by_project(...)` in this Service feature.

The current `IssueService.list_issues()` contract returns:

```python
list[IssueSummaryResponse]
```

It does not return `total`, `page`, or `page_size`.

Construction of the API pagination response, including `total`, belongs to the later API Layer. `IssueRepository.count_by_project(...)` remains available for that later feature and must not be removed or modified here.

Preserve Repository ordering:

```text
updated_at DESC
id DESC
```

Do not commit.

---

## Issue Detail

Requirements:

- Retrieve the Issue through `IssueRepository.find_by_id(issue_id)`.
- Raise `NotFoundError` when it does not exist.
- Retrieve Comments through `CommentRepository.list_by_issue(issue_id)` when required for detail output.
- Retrieve Attachments through `AttachmentRepository.list_by_issue(issue_id)` when required for detail output.
- Preserve Repository ordering:
  - Comments: `created_at ASC, id ASC`
  - Attachments: `uploaded_at ASC, id ASC`
- Do not commit.

Do not add new Repository eager-loading behavior unless a demonstrated query problem requires it and the change is separately approved.

---

## Create Issue

### Required existence checks

Before creating the Issue:

- Project must exist.
- User identified by `user_id` must exist.
- Room must exist when `room_id` is supplied.
- When a Room is supplied, the Room must belong to the Project's Hotel.

Raise `NotFoundError` for a missing Project, User, or Room.

Use the Project's related Hotel information already loaded by `ProjectRepository`.

### Allowed Target Types

Only:

```text
ROOM
OTHER
```

### Target consistency rules

For `ROOM`:

- `room_id` is required.
- `target` must be `None`.
- The Room must belong to the Project's Hotel.

For `OTHER`:

- `room_id` must be `None`.
- `target` is required.
- `target` must not be empty after applying the input-normalization behavior already defined by the schema.

Invalid combinations raise `ValidationError`.

Do not add a database CHECK constraint.

### Category

Allow only the Category values defined by the current model and design.

Do not maintain a second hard-coded list if the current enum can be used safely as the source.

Invalid Category raises `ValidationError`.

### Description

Description is required and must not be empty.

Respect any whitespace normalization already performed by the schema. Do not invent additional text transformation.

An empty Description raises `ValidationError`.

### Initial Status

New Issues must start with `OPEN`.

`CreateIssueRequest` does not contain a Status field.

`IssueService.create_issue()` must explicitly set `status=Status.OPEN`.

Do not accept a caller-controlled initial Status.

Do not add a Model default or Database default for this behavior.
The Service Layer owns the initial Status rule.

### Entity creation

Construct an `Issue` using the existing model fields.

Set:

- Project
- Room or target according to Target Type
- Target Type
- Category
- Description
- Initial Status
- Creator
- Updater
- Created timestamp
- Updated timestamp

Call `IssueRepository.create(issue)`.

After successful Repository creation:

- Commit once.
- Return the created Issue ID.
- Do not return an uncommitted ID.
- Do not create Comments or Attachments in the same method.

On any exception:

- Roll back.
- Re-raise.

---

## Update Issue

Requirements:

- Issue must exist.
- User identified by `user_id` must exist.
- Validate the Room, Target Type, Target, Category, and Description fields defined by `UpdateIssueRequest`.
- Do not make immutable fields editable.
- `UpdateIssueRequest` represents the current `PUT` API and all request fields are required.
- `room_id` and `target` may explicitly be `None`.
- Validate the submitted final state, including cross-field Target consistency.
- If the final state uses a Room, verify that the Room belongs to the Issue Project's Hotel.
- Update `updated_by` or equivalent updater relationship/field.
- Update `updated_at` according to the timestamp policy.
- Call `IssueRepository.update(issue)`.
- Commit once.
- Return `None`.

On any exception:

- Roll back.
- Re-raise.

Do not copy update rules into the Repository.

If the current model field names differ from the design terminology, use the actual model fields and report any material mismatch.

---

## Update Status

Requirements:

- Issue must exist.
- User identified by `user_id` must exist.
- Status must be a defined Status value.
- Update only Status and the required updater/timestamp fields.
- Do not implement undocumented status-transition restrictions.
- Call `IssueRepository.update(issue)`.
- Commit once.
- Return `None`.

Invalid Status raises `ValidationError`.

On any exception:

- Roll back.
- Re-raise.

---

## Validation Helpers

Private helper methods are allowed when they make business rules easier to read and test.

Reasonable examples:

```python
_validate_target(...)
_validate_category(...)
_validate_status(...)
_validate_room_matches_project(...)
_require_project(...)
_require_room(...)
_require_issue(...)
_require_user(...)
```

Rules:

- Helpers must remain private to the Service unless the detailed design explicitly defines a public validation method.
- Do not create a generic validation framework.
- Do not create utility modules for one-off checks.
- Do not duplicate enum definitions.
- Keep exception mapping consistent.

---

# CommentService

## Responsibilities

- Verify that the Issue exists.
- Verify that the User exists.
- Validate Comment content.
- Create a Comment.
- Complete the transaction.

## Dependencies

Use only:

- `IssueRepository`
- `UserRepository`
- `CommentRepository`
- SQLAlchemy `Session`

## Method

Implement the signature defined by the current detailed design and schemas.

Expected conceptual operation:

```python
create_comment(
    issue_id: int,
    request: CreateCommentRequest,
    user_id: int,
) -> int
```

Requirements:

- Retrieve the Issue through `IssueRepository.find_by_id(issue_id)`.
- Raise `NotFoundError` when the Issue does not exist.
- Retrieve the User through `UserRepository.find_by_id(user_id)`.
- Raise `NotFoundError` when the User does not exist.
- Comment text is required and must not be empty.
- Respect schema-level whitespace normalization.
- Invalid or empty Comment raises `ValidationError`.
- Construct a `Comment` using the existing model fields.
- Set Issue, creator, Comment text, and created timestamp.
- Call `CommentRepository.create(comment)`.
- Commit once.
- Return the created Comment ID.
- Do not implement Comment update or delete.
- Do not commit any other entity changes.

On any exception:

- Roll back.
- Re-raise.

---

# Service Package Exports

Update `app/services/__init__.py` only as needed to expose:

- `ProjectService`
- `IssueService`
- `CommentService`

Use one module docstring.

Do not export out-of-scope placeholder Services.

Do not add empty implementations for future Services.

---

# Tests

## Test Strategy

Use unit tests for Service business logic.

Repository dependencies must be mocked or replaced with simple test doubles. Service tests must not require an actual SQLite database.

The Repository integration behavior has already been tested in `tests/repositories`.

Use the real domain model classes and enums where practical.

Mock only boundaries that the Service calls.

Tests must verify:

- Returned values
- Entity mutations
- Repository calls
- Commit behavior
- Rollback behavior
- Raised application exceptions
- No commit on read-only methods

Do not test private helper methods directly when their behavior is covered through public methods.

Do not assert internal implementation details that are not part of Service behavior.

---

## ProjectService Tests

Cover at minimum:

- Project list success
- Repository order is preserved
- Project exists
- Project not found raises `NotFoundError`
- Read methods do not commit

Do not invent user-based Project filtering tests.

---

## IssueService Tests

Cover at minimum:

### List and detail

- List Issues success
- Correct page-to-offset conversion
- `page < 1` is rejected
- `page_size < 1` is rejected
- Filters are passed unchanged to `IssueRepository.list_by_project(...)`
- `IssueRepository.count_by_project(...)` is not called by `IssueService.list_issues()`
- Project not found
- Issue detail success
- Issue detail not found
- Comment and Attachment order is preserved when included
- Read methods do not commit

### Create

- Create Issue with `ROOM`
- Create Issue with `OTHER`
- New Issue starts with `Status.OPEN`
- Generated ID is returned after successful commit
- Project not found
- User not found
- Room not found
- Room belongs to a different Hotel
- Invalid Target Type
- `ROOM` without Room
- `ROOM` with Target
- `OTHER` without Target
- `OTHER` with Room
- Invalid Category
- Empty Description
- Successful create commits once
- Repository failure rolls back
- Validation failure does not commit
- Validation failure does not call Repository create

### Update

- Successful update
- Final-state Target validation
- Room/Project Hotel mismatch
- Invalid Category
- Empty Description
- User not found
- Issue not found
- Successful update commits once
- Repository failure rolls back
- Validation failure does not commit

### Status

- Successful Status update
- Invalid Status
- Issue not found
- User not found
- Only allowed fields are changed
- Successful update commits once
- Repository failure rolls back

Do not add undocumented status-transition tests.

---

## CommentService Tests

Cover at minimum:

- Successful Comment creation
- Created Comment ID is returned
- Issue not found
- User not found
- Empty Comment
- Successful create commits once
- Repository failure rolls back
- Validation failure does not commit
- Validation failure does not call Repository create

---

## Test Style

Follow existing project conventions.

Prefer clear individual tests over one very large test containing unrelated assertions.

Long test setup may be moved into fixtures or small helper functions, but do not create a test framework.

Do not import a helper function from another test module when a local fixture or shared `conftest.py` helper is clearer and avoids test-module coupling.

---

# Required Verification

Run from `backend/`:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/services
```

Then run:

```bash
git diff --check
```

Then attempt the full test suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

If the full test suite encounters the already known timeout in `test_application_error_uses_common_response`:

- Report the timeout accurately.
- Confirm whether the new Service tests passed independently.
- Do not modify the unrelated API exception-handler test in this feature.
- Do not claim that the full suite passed.

Run the project's configured linter or formatter only if it is already available in project dependencies or documented commands.

Do not add a new dependency only to run formatting.

---

# Completion Report

When implementation is complete, report:

## Summary

- Services implemented
- Tests added

## Modified Files

List every modified and new file.

## Service Methods

List the implemented public methods for each Service.

## Validation Behavior

Summarize:

- Existence checks
- Target Type rules
- Room/Project Hotel matching
- Category validation
- Status validation
- Description validation
- Comment validation

## Transaction Behavior

Confirm:

- Read operations do not commit
- Successful writes commit once
- Failed writes roll back
- Services do not call `flush()` directly
- Repositories do not define transaction completion

## Tests

Report each executed command and exact result.

## Design Compliance

Confirm:

- No direct SQLAlchemy queries in Services
- No API, Auth, AI, Attachment, Storage, schema, model, migration, or frontend changes
- No undocumented authorization or status-transition rules
- No unrelated refactoring

## Issues or Ambiguities

List any unresolved issue. If none, state that none remain.

## Remaining Work

State that Auth, AI, Attachment, Storage, and API implementation remain outside this feature.

---

# Stop Conditions

Stop and report before continuing if any of the following is found:

- Required request or response schema classes do not exist.
- Schema fields conflict with the latest design.
- Service return types are contradictory between detailed design, API design, and existing schemas.
- The initial Issue Status is not consistently defined.
- Existing exception constructors or required error codes are unclear.
- Project-to-Hotel or Room-to-Hotel relationships differ from the documented model.
- Existing Repository methods cannot support the defined Service behavior.
- An implementation would require adding direct database queries to a Service.
- A required validation rule is not defined.
- A write operation cannot be made atomic with the current Session and Repository design.
- Implementing the feature requires changing a migration or database model.
- Auth, AI, upload, or file-storage logic becomes necessary for a core Service.
- Any unrelated failure would require changing code outside this feature.

Do not resolve design ambiguity by guessing.
