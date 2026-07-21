# Repository Layer Implementation Guide

## Feature

`feature/repositories`

---

## Purpose

Implement the Repository Layer for the Commissioning Issue Manager (CIM).

This feature provides database access through SQLAlchemy repositories while preserving the responsibilities defined by the layered architecture.

Repository classes must perform database access only. Business rules, validation, authorization, DTO conversion, and transaction completion must not be implemented in this feature.

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

Follow the source-of-truth priority defined in `AGENTS.md`.

If the documents and existing implementation conflict, do not guess or silently change the design. Report the inconsistency and stop the affected work until it is clarified.

Do not modify design documents in this feature.

---

## Scope

Implement only:

- Repository classes
- Repository package initialization where necessary
- Shared repository query code only when it clearly removes duplication
- Repository tests using an actual SQLite test database
- Minimal test fixtures required for repository tests

Implement the following repositories:

- `UserRepository`
- `ProjectRepository`
- `RoomRepository`
- `IssueRepository`
- `CommentRepository`
- `AttachmentRepository`

Do not implement a dedicated `HotelRepository`.

In the initial version, Hotel information is retrieved together with Project data.

---

## Expected Directory Structure

Follow the existing project structure. Use the following structure unless the repository already establishes an equivalent convention:

```text
backend/
├── app/
│   └── repositories/
│       ├── __init__.py
│       ├── user_repository.py
│       ├── project_repository.py
│       ├── room_repository.py
│       ├── issue_repository.py
│       ├── comment_repository.py
│       └── attachment_repository.py
└── tests/
    └── repositories/
        ├── __init__.py
        ├── conftest.py
        ├── test_user_repository.py
        ├── test_project_repository.py
        ├── test_room_repository.py
        ├── test_issue_repository.py
        ├── test_comment_repository.py
        └── test_attachment_repository.py
```

Do not move or rename existing files unnecessarily.

---

## Common Repository Rules

Each repository must:

- Receive a SQLAlchemy `Session` through constructor injection.
- Use SQLAlchemy 2.x query APIs.
- Return SQLAlchemy entities, not dictionaries or Pydantic DTOs.
- Return `None` when a single entity is not found.
- Contain database access only.
- Use type hints.
- Follow the existing synchronous database access style.

Example constructor:

```python
class IssueRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
```

Repositories must not:

- Perform business validation.
- Perform authorization.
- Raise HTTP exceptions.
- Convert entities to API response DTOs.
- Call Service classes.
- Create their own database sessions.
- Call `commit()`.
- Call `rollback()`.
- Define transaction boundaries.
- Change the database schema.
- Add undocumented repository methods.
- Add a generic base repository unless it is already required by the current design.

The Service Layer owns transaction completion.

---

## Flush Policy

Repositories may call `flush()` when a write method must synchronize the current unit of work with the database before returning.

### Create

After `create()` returns:

- The entity must have its database-generated ID assigned.
- The entity must remain part of the current uncommitted transaction.
- The repository must not commit the transaction.

Use `session.add(entity)` followed by `session.flush()`.

Use `refresh()` only when required to load database-generated values that are not already populated after `flush()`.

### Update

After `update()` returns:

- Pending changes must have been flushed to the database.
- The transaction must remain uncommitted.
- The same persistent entity may be returned.

Do not copy fields, perform validation, or decide which fields are editable in the repository. The Service Layer is responsible for modifying the entity before calling `update()`.

### Delete

`AttachmentRepository.delete()` must mark the supplied entity for deletion and flush the change without committing.

---

## UserRepository

Implement:

```python
find_by_id(user_id: int) -> User | None

find_by_username(username: str) -> User | None
```

Requirements:

- `find_by_id()` retrieves a User by primary key.
- `find_by_username()` retrieves a User by exact username.
- Do not add password hashing or password verification.
- Do not add login, token generation, authorization, or session handling.

Password hashing and verification are not Repository responsibilities. They will be implemented later in a Security Utility during the authentication implementation phase.

---

## ProjectRepository

Implement:

```python
find_by_id(project_id: int) -> Project | None

list_all() -> list[Project]
```

Requirements:

- Project results must include their related Hotel information.
- Load Hotel data in a way that avoids unnecessary additional queries when the caller accesses `project.hotel`.
- Do not implement `HotelRepository`.
- Do not add `list_by_hotel()` or other undocumented Project methods in this feature.
- Use a deterministic order for `list_all()` based on the current design or existing implementation. If no order is defined, do not invent a business-specific order; use a stable primary-key order and report that choice in the completion summary.

---

## RoomRepository

Implement:

```python
find_by_id(room_id: int) -> Room | None

find_by_hotel_and_room_number(
    hotel_id: int,
    room_number: str
) -> Room | None

list_by_hotel(hotel_id: int) -> list[Room]
```

Requirements:

- Match both `hotel_id` and exact `room_number` in `find_by_hotel_and_room_number()`.
- `list_by_hotel()` returns only Rooms belonging to the specified Hotel.
- Do not add free-text Room search.
- Do not add Room-name or partial Room-number search.
- Use a deterministic order based on the current design. If no order is defined, use a stable primary-key order and report that choice.

---

## IssueRepository

Implement:

```python
find_by_id(issue_id: int) -> Issue | None

list_by_project(
    project_id: int,
    status: str | None,
    category: str | None,
    target_type: str | None,
    keyword: str | None,
    offset: int,
    limit: int
) -> list[Issue]

count_by_project(
    project_id: int,
    status: str | None,
    category: str | None,
    target_type: str | None,
    keyword: str | None
) -> int

create(issue: Issue) -> Issue

update(issue: Issue) -> Issue
```

### Filtering

`list_by_project()` and `count_by_project()` must apply the same filtering rules:

- Always filter by `project_id`.
- Apply the Status filter only when `status` is not `None`.
- Apply the Category filter only when `category` is not `None`.
- Apply the Target Type filter only when `target_type` is not `None`.
- Apply keyword search only when `keyword` is not `None`.
- Keyword search targets Issue description as defined by the Test Design.
- Do not perform business validation of filter values in the repository.
- Do not silently normalize undocumented values.

A small private query-construction helper may be used so that list and count cannot drift apart. Keep it local to `IssueRepository`; do not create unnecessary abstractions.

### Pagination

For `list_by_project()`:

- `offset` is the number of matching records to skip.
- `limit` is the maximum number of matching records to return.
- Apply filtering before offset and limit.
- Do not calculate or return total count from this method.
- Do not validate allowed offset or limit ranges; that belongs to the API or Service Layer.

### Count

For `count_by_project()`:

- Return the total number of records matching the same Project and optional filters.
- Do not apply offset or limit.
- Execute a database count query rather than loading all matching entities into Python.
- Return an integer.

### Sort Order

Issue lists must be returned in `updated_at` descending order, with the most recently updated Issue first.

Add a deterministic tie-breaker using primary key descending when multiple Issues have the same `updated_at`.

### Create

`create(issue)` must:

```text
add entity
→ flush
→ return persistent entity with ID
```

It must not commit.

### Update

`update(issue)` must:

```text
flush pending changes
→ return persistent entity
```

It must not commit.

The repository must not decide which fields are changed.

---

## CommentRepository

Implement:

```python
list_by_issue(issue_id: int) -> list[Comment]

create(comment: Comment) -> Comment
```

Requirements:

- Return only Comments belonging to the specified Issue.
- Use the ordering defined by the current design.
- If no ordering is defined, use `created_at` ascending with primary key ascending as a deterministic tie-breaker and report the choice.
- `create()` must add and flush the Comment so its ID is assigned.
- Do not commit.

---

## AttachmentRepository

Implement:

```python
find_by_id(attachment_id: int) -> Attachment | None

list_by_issue(issue_id: int) -> list[Attachment]

create(attachment: Attachment) -> Attachment

delete(attachment: Attachment) -> None
```

Requirements:

- Return only Attachments belonging to the specified Issue.
- Use the ordering defined by the current design.
- If no ordering is defined, use `uploaded_at` ascending with primary key ascending as a deterministic tie-breaker and report the choice.
- `create()` must add and flush the Attachment so its ID is assigned.
- `delete()` must delete and flush the supplied Attachment.
- Do not delete the physical file from storage.
- Do not call `StorageService`.
- Do not commit.

---

## Relationship Loading

Use explicit eager loading only where required by the approved design or necessary to prevent an immediately predictable N+1 query.

Required in this feature:

- Project retrieval includes Hotel information.

Do not eagerly load every relationship by default.

In particular, do not automatically load full Issue aggregates, Comments, or Attachments unless the current design explicitly requires that behavior for the repository method.

Do not modify relationship definitions in the models unless an actual defect prevents repository implementation. Report such a defect before changing model design.

---

## Testing

Use an actual SQLite test database.

Do not mock SQLAlchemy for Repository tests.

Reuse existing database fixtures where appropriate. Keep tests isolated and deterministic.

Run all tests from the `backend` directory:

```bash
uv run pytest
```

Also run the Repository tests separately:

```bash
uv run pytest tests/repositories
```

Adjust only the test path if the existing project uses a different established test directory.

### Common Tests

Verify where applicable:

- Existing entity can be found.
- Missing entity returns `None`.
- Create adds an entity.
- Update flushes changes.
- Delete removes only the supplied entity.
- List methods return only matching entities.
- No repository method commits the transaction.

### UserRepository Tests

Verify:

- Find by ID.
- Missing ID.
- Find by username.
- Missing username.

Do not test password hashing or password verification in Repository tests.

### ProjectRepository Tests

Verify:

- Find by ID.
- Missing ID.
- List all.
- Hotel relationship is available with returned Project entities.
- No dedicated HotelRepository is introduced.

Where practical, verify that accessing `project.hotel` does not trigger one additional query for every returned Project.

### RoomRepository Tests

Verify:

- Find by ID.
- Missing ID.
- Find by Hotel and Room Number.
- Same Room Number in a different Hotel is not returned.
- List by Hotel excludes Rooms from other Hotels.

### IssueRepository Tests

Verify:

- Find by ID.
- Missing ID.
- List by Project.
- Status filter.
- Category filter.
- Target Type filter.
- Keyword search against description.
- Combined filters.
- Offset and limit pagination.
- `count_by_project()` without optional filters.
- `count_by_project()` with each filter.
- `count_by_project()` with combined filters.
- Count is not affected by list pagination.
- Sort by `updated_at` descending.
- Deterministic ordering when `updated_at` values are equal.
- `create()` returns an Issue whose ID is not `None` after flush.
- `create()` does not commit.
- `update()` flushes the changed value to the current transaction.
- `update()` does not commit.

To verify flush behavior, use another query within the same transaction or expire/refresh the entity as appropriate. Do not commit merely to make the assertion pass.

To verify that repositories do not commit, use a rollback after the repository call and confirm that the write is not present afterward.

### CommentRepository Tests

Verify:

- List by Issue.
- Comments from other Issues are excluded.
- Create assigns an ID after flush.
- Create does not commit.
- Deterministic ordering (`created_at` ascending, then primary key ascending).

### AttachmentRepository Tests

Verify:

- Find by ID.
- Missing ID.
- List by Issue.
- Attachments from other Issues are excluded.
- Create assigns an ID after flush.
- Delete flushes removal.
- Delete affects only the supplied Attachment.
- Create and delete do not commit.
- Deterministic ordering (`uploaded_at` ascending, then primary key ascending).

---

## Existing Tests and Fixtures

Review the existing model and migration tests before adding fixtures.

Do not duplicate the entire model setup when a small reusable factory or fixture is sufficient.

Do not weaken, delete, skip, or rewrite existing tests to make this implementation pass.

Do not change the production database.

---

## Out of Scope

Do not implement:

- Service classes
- API routers or endpoints
- Pydantic schemas
- Authentication flow
- Password hashing or password verification
- Security Utility implementation
- Authorization
- Token generation
- Transaction middleware
- HotelRepository
- Hotel management
- Project filtering by Hotel
- Room free-text search
- Business validation
- Target Type consistency validation
- Category or Status validation
- Attachment file storage or deletion
- AI integration
- Frontend changes
- Database migrations
- Database schema changes
- Unrelated refactoring
- New development tools or dependency upgrades

---

## Dependencies

Do not add or upgrade dependencies unless an existing approved design cannot be implemented without one.

Before adding any package:

- Check existing dependencies and security utilities.
- Explain why it is required.
- Keep the change limited to this feature.

Do not introduce Ruff, mypy, Docker, or unrelated tooling.

---

## Git Rules

- Work only on `feature/repositories`.
- Do not switch branches.
- Do not commit.
- Do not push.
- Do not merge.
- Do not create a Pull Request.
- Do not rewrite Git history.
- Do not force-push.

---

## Acceptance Criteria

- All six designed Repository classes are implemented.
- No `HotelRepository` is created.
- Project retrieval includes Hotel information.
- Repository classes use injected SQLAlchemy Sessions.
- Repository methods return SQLAlchemy entities.
- Issue filters behave consistently between list and count.
- Issue pagination correctly applies offset and limit.
- Issue count executes as a count query and ignores pagination.
- Issue list order is `updated_at` descending with a deterministic tie-breaker.
- Create methods flush and return entities with assigned IDs.
- Issue update flushes pending changes.
- Attachment delete flushes deletion.
- No repository method commits or rolls back.
- No business logic or validation is added.
- Repository tests use an actual SQLite database.
- Repository tests pass.
- Existing tests pass.
- No database migration or schema change is introduced.
- No unrelated files are modified.

---

## Stop Conditions

Stop and report before implementation if:

- Current documents define conflicting Repository methods or responsibilities.
- Existing models do not support the documented queries.
- Implementing the repositories requires a database schema change.
- The branch is not `feature/repositories`.
- Existing failures prevent reliable verification.
- A required design decision would have to be guessed.

Do not resolve these issues by silently changing design documents or architecture.

---

## Completion Report

Report using this structure:

### Summary

Briefly describe what was implemented.

### Modified Files

List created and modified files.

### Repository Methods

Summarize the methods implemented for each Repository.

### Query Behavior

Describe:

- Project and Hotel loading
- Issue filters
- Issue offset and limit
- Issue count
- Sort order

### Write Behavior

Confirm:

- IDs are assigned after create and flush
- Updates are flushed
- Deletes are flushed
- No Repository commits or rolls back

### Tests

List the commands executed and their results.

### Design Compliance

Confirm compliance with:

- Repository responsibilities
- No HotelRepository
- No business logic
- No schema or migration changes
- No unrelated changes

### Issues or Ambiguities

List any unresolved items. Write `None` when there are none.

### Remaining Work

State that Service Layer and API implementation remain out of scope for this feature.

---

## Notes

This feature establishes only the Repository Layer.

The Service Layer will later be responsible for:

- Business validation
- Authorization
- Coordinating multiple repositories
- Transaction commit and rollback
- DTO conversion support

Keep the implementation small, direct, and consistent with the approved design.
