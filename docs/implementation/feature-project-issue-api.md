# Project / Issue API Integration Implementation Guide

## Purpose

Implement the Project and Issue HTTP API layer for the Commissioning Issue Manager (CIM).

This feature connects the existing authentication, Service, Repository, Model, and Schema foundations to the approved Project and Issue REST API contracts.

The implementation must remain documentation-first, minimal, and consistent with the existing layered architecture.

---

# Implementation Scope

Implement the following authenticated endpoints.

## Project API

```http
GET /api/projects
```

## Issue API

```http
GET /api/projects/{project_id}/issues
GET /api/issues/{issue_id}
POST /api/projects/{project_id}/issues
PUT /api/issues/{issue_id}
PATCH /api/issues/{issue_id}/status
```

The feature includes:

- Project and Issue API Router modules
- FastAPI Dependency construction for `ProjectService` and `IssueService`
- Router registration
- Authentication integration using the existing `get_current_user` Dependency
- Request and query parameter handling
- Response conversion required by the approved API contract
- `IssueListResponse` implementation and integration
- Minimal Service changes required for the approved paginated Issue list contract
- Project and Issue API integration tests
- Focused regression tests for any changed Service or Schema behavior

---

# Source of Truth

Read the latest project documents before changing code.

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

Also inspect the existing implementation before editing:

- `backend/app/api/deps.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`
- `backend/app/schemas/project.py`
- `backend/app/schemas/issue.py`
- `backend/app/services/project_service.py`
- `backend/app/services/issue_service.py`
- `backend/app/repositories/project_repository.py`
- `backend/app/repositories/issue_repository.py`
- related existing tests

If the current repository structure differs from these paths, follow the actual current structure and the latest Detailed Design. Do not create duplicate modules.

---

# Branch and Git Rules

Work only on the assigned feature branch.

Do not:

- switch branches without instruction
- merge branches
- rewrite history
- force push
- commit
- push
- modify unrelated files
- discard or overwrite existing user changes

Preserve all pre-existing modified and untracked files.

---

# Architecture Rules

The existing layered architecture must be preserved.

```text
HTTP Request
    │
    ▼
API Router
    │
    ▼
Service
    │
    ▼
Repository
    │
    ▼
Database
```

## API Router Responsibilities

The API Router may perform only HTTP-layer work:

- receive path, query, and body parameters
- receive the authenticated user through Dependency Injection
- call the appropriate Service method
- construct the exact public response required by API Design
- declare the public response model when appropriate

The API Router must not:

- execute SQLAlchemy queries
- instantiate SQLAlchemy queries
- call Repository methods directly
- implement Project or Issue business validation
- calculate database totals independently
- manage commit or rollback
- duplicate Service validation
- infer undocumented defaults or behavior

## Service Responsibilities

The Service Layer owns:

- business validation
- Project, Issue, Room, and User existence checks already assigned by design
- Target Type and Room / Target consistency
- Category and Status validation
- transaction management for writes
- Repository coordination
- Entity-to-DTO conversion where already defined
- paginated Issue list response generation required by Detailed Design

## Repository Responsibilities

Repository remains data-access-only.

Do not add:

- business validation
- HTTP behavior
- response DTO construction
- authentication behavior
- transaction ownership

Repository methods must not commit or rollback.

---

# Authentication and Authorization

All endpoints in this feature require authentication.

Use the existing authentication Dependency.

```python
CurrentUserDependency
```

or the equivalent existing alias based on:

```python
get_current_user()
```

Do not implement a second authentication path.

Do not:

- read or verify passwords in these routes
- parse the Session manually in each route
- add JWT or Bearer authentication
- add role restrictions not defined by the authorization matrix
- require Administrator for Project or Issue APIs

Both `ADMINISTRATOR` and `ENGINEER` may use all Project and Issue endpoints in this feature.

For write operations, pass the authenticated user's ID to the existing Service method.

```python
current_user.id
```

Use the authenticated user as follows:

|Endpoint|Service user ID|
|---|---|
|`GET /api/projects`|Pass to `ProjectService.list_projects()` if required by its approved contract|
|`GET /api/projects/{project_id}/issues`|Do not add a user parameter unless the approved current Service contract requires it|
|`GET /api/issues/{issue_id}`|Do not add a user parameter unless the approved current Service contract requires it|
|`POST /api/projects/{project_id}/issues`|Pass `current_user.id`|
|`PUT /api/issues/{issue_id}`|Pass `current_user.id`|
|`PATCH /api/issues/{issue_id}/status`|Pass `current_user.id`|

Do not add new authorization logic inside `ProjectService` or `IssueService` unless it is already required by the latest design.

---

# Service Dependency Construction

Add or extend FastAPI dependencies in the existing dependency module.

Expected responsibilities:

```python
get_project_service(...)
get_issue_service(...)
```

Construct Services using existing Repository classes and the request-scoped SQLAlchemy Session.

Conceptually:

```text
Database Session
    ├── ProjectRepository
    ├── RoomRepository
    ├── IssueRepository
    ├── CommentRepository
    ├── AttachmentRepository
    └── UserRepository when required by the existing Service constructor
```

Follow the actual constructors in the current code.

Do not:

- redesign Service constructors without necessity
- add a generic service container
- add a new dependency-injection framework
- create repositories that are not required by the current Service contract
- perform database queries in dependency functions

Export Dependency aliases consistently with the existing authentication implementation.

---

# Schema Requirements

Use the existing public Request and Response DTOs wherever present.

The approved Detailed Design includes:

```python
ProjectResponse
ProjectListResponse
CreateIssueRequest
UpdateIssueRequest
UpdateIssueStatusRequest
IssueSummaryResponse
IssueListResponse
IssueDetailResponse
CommentResponse
AttachmentResponse
```

## IssueListResponse

Ensure the public Issue list response DTO exists and contains exactly:

```python
items: list[IssueSummaryResponse]
page: int
page_size: int
total: int
```

Do not add extra fields such as:

- `pages`
- `next`
- `previous`
- `has_next`
- `has_previous`

Do not expose SQLAlchemy Models directly.

Use the current project's Pydantic conventions, including any existing `ConfigDict`, `from_attributes`, nested DTO types, or field aliases.

Do not alter unrelated public DTOs.

---

# Project API

## GET `/api/projects`

### Authentication

Required.

### Behavior

Call the existing:

```python
ProjectService.list_projects(user_id)
```

using the authenticated user's ID if that remains the current approved Service signature.

Return the exact API shape:

```json
{
  "projects": [
    {
      "id": 1,
      "name": "Hotel A Commissioning",
      "hotel": {
        "id": 1,
        "name": "Hotel A"
      }
    }
  ]
}
```

### Error Behavior

- unauthenticated: `401 Unauthorized`

Do not add Project management, Project creation, update, or deletion APIs.

Do not filter Projects by invented ownership or Hotel membership rules.

---

# Issue List API

## GET `/api/projects/{project_id}/issues`

### Authentication

Required.

### Path Parameter

```python
project_id: int
```

### Query Parameters

The approved API accepts:

```text
status
category
target_type
keyword
page
page_size
```

Pass query values to `IssueService.list_issues()` without silently trimming, translating, normalizing, or changing their meaning unless current approved Service behavior already does so.

### Sorting

The result must follow the approved Repository/API behavior:

```text
updated_at descending
```

Do not sort again in the Router.

### Filters

Support the approved filters:

- Status
- Category
- Target Type
- Description keyword
- combined filters

Do not add:

- Room filters
- created-by filters
- date-range filters
- Hotel filters
- full-text search
- fuzzy search

### Pagination

The response must be:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

The Service must return `IssueListResponse`.

The Service may coordinate:

```python
IssueRepository.list_by_project(...)
IssueRepository.count_by_project(...)
```

to produce the approved response, if this is not already implemented.

The Router must not call either Repository directly.

## Pagination Defaults and Bounds

The API Design marks `page` and `page_size` as optional but does not, by itself, fully define normative defaults and bounds.

Before implementing defaults or limits:

1. inspect the current `IssueService`
2. inspect existing Schema definitions
3. inspect existing Service and Repository tests
4. inspect prior approved implementation documentation in the repository

If the current approved implementation already defines unambiguous defaults and validation, preserve them.

If no approved source unambiguously defines:

- default `page`
- default `page_size`
- minimum values
- maximum `page_size`
- error behavior for out-of-range values

stop and report the ambiguity before continuing. Do not infer those values solely from an example response.

### Error Behavior

- invalid approved filter or pagination input: use the existing project validation/error flow
- unauthenticated: `401 Unauthorized`
- Project not found: `404 Not Found`

Do not manually build custom error JSON in the Router. Use existing project exceptions and handlers.

---

# Issue Detail API

## GET `/api/issues/{issue_id}`

### Authentication

Required.

### Behavior

Call:

```python
IssueService.get_issue_detail(issue_id)
```

Return the approved `IssueDetailResponse`.

The response includes:

- Issue core fields
- Project summary
- optional Room summary
- creator summary
- updater summary
- Comment list
- Attachment list

Do not:

- query CommentRepository from the Router
- query AttachmentRepository from the Router
- load or open physical attachment files
- add download URLs unless already part of the approved DTO
- add fields not defined by API Design

### Error Behavior

- unauthenticated: `401 Unauthorized`
- Issue not found: `404 Not Found`

---

# Create Issue API

## POST `/api/projects/{project_id}/issues`

### Authentication

Required.

### Request

Use the existing `CreateIssueRequest`.

ROOM request:

```json
{
  "room_id": 1,
  "target_type": "ROOM",
  "category": "LIGHTING",
  "description": "Bathroom light does not turn off."
}
```

OTHER request:

```json
{
  "room_id": null,
  "target_type": "OTHER",
  "target": "Network",
  "category": "NETWORK",
  "description": "Processor cannot communicate with gateway."
}
```

### Behavior

Call:

```python
IssueService.create_issue(
    project_id=project_id,
    request=request,
    user_id=current_user.id,
)
```

The Service sets the initial Status to `OPEN`.

Do not accept Status in `CreateIssueRequest`.

Do not rely on Model or Database defaults for Status.

### Response

Return exactly:

```json
{
  "id": 101,
  "message": "Issue created"
}
```

Use the ID returned by the Service.

Do not fetch the created Issue again unless an existing approved contract requires it.

### Error Behavior

- invalid input or business validation: `400 Bad Request`
- unauthenticated: `401 Unauthorized`
- Project or required referenced resource not found: use the existing approved exception mapping

Do not convert Project-not-found into a generic success or empty result.

---

# Update Issue API

## PUT `/api/issues/{issue_id}`

### Authentication

Required.

### Request

Use the existing `UpdateIssueRequest`.

The request updates:

- `room_id`
- `target_type`
- `target`
- `category`
- `description`

Status is not updated through this endpoint.

### Behavior

Call:

```python
IssueService.update_issue(
    issue_id=issue_id,
    request=request,
    user_id=current_user.id,
)
```

### Response

Return exactly:

```json
{
  "id": 101,
  "message": "Issue updated"
}
```

Do not return a full Issue object unless API Design is changed first.

### Error Behavior

- invalid input or business validation: `400 Bad Request`
- unauthenticated: `401 Unauthorized`
- Issue not found: `404 Not Found`

---

# Update Issue Status API

## PATCH `/api/issues/{issue_id}/status`

### Authentication

Required.

### Request

Use the existing `UpdateIssueStatusRequest`.

```json
{
  "status": "IN_PROGRESS"
}
```

Allowed values are the existing Status enum values:

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

### Behavior

Call:

```python
IssueService.update_status(
    issue_id=issue_id,
    request=request,
    user_id=current_user.id,
)
```

### Response

Return exactly:

```json
{
  "id": 101,
  "status": "IN_PROGRESS",
  "message": "Status updated"
}
```

Use the validated/requested Status value only if the Service completed successfully.

Do not modify any other Issue fields.

### Error Behavior

- invalid Status: `400 Bad Request`
- unauthenticated: `401 Unauthorized`
- Issue not found: `404 Not Found`

---

# Router Structure

Use the approved modules:

```text
backend/app/api/routes/projects.py
backend/app/api/routes/issues.py
```

Follow existing Router conventions.

Recommended route prefixes:

```python
APIRouter(prefix="/api/projects", tags=["projects"])
APIRouter(prefix="/api/issues", tags=["issues"])
```

Equivalent routing is acceptable only if it preserves the exact public paths and current project style.

Register both Routers through the existing route package and application factory.

Do not:

- place Project and Issue endpoints in `auth.py`
- duplicate the `/api` prefix
- create a second FastAPI application
- change SessionMiddleware
- change authentication routes
- register unrelated routes

---

# Response Construction Policy

API Design owns the public JSON contract.

Detailed Design assigns business DTO conversion to the Service where defined, while the API Router remains responsible for the final endpoint-specific response envelope or message.

Examples:

```python
{"id": issue_id, "message": "Issue created"}
```

```python
{
    "id": issue_id,
    "status": request.status,
    "message": "Status updated",
}
```

Do not move Repository coordination into the Router in the name of response construction.

Do not expose:

- password hashes
- SQLAlchemy internal state
- raw relationships
- storage paths
- internal exception details

---

# Transaction Policy

Read endpoints must not commit.

Write transaction ownership remains in `IssueService`.

Expected write operations:

```text
Create Issue
Update Issue
Update Status
```

The Router must not call:

```python
session.commit()
session.rollback()
session.flush()
```

Repository methods must not take ownership of commit or rollback.

Preserve existing rollback behavior.

---

# Validation Policy

Use Pydantic for:

- request field presence
- request field type
- query parameter type where defined by FastAPI/Pydantic

Use `IssueService` for:

- Project existence
- Issue existence
- Room existence
- Room and Project Hotel consistency
- Target Type validity
- ROOM / OTHER consistency
- Category validity
- Status validity
- Description business validation
- pagination business validation when defined

Do not duplicate Enum validation in the Router if the current Service owns it.

Do not silently coerce invalid Enum values.

Do not trim, translate, normalize, or fill missing Issue values unless already required by approved design.

---

# Error Handling

Use existing project-specific exceptions:

- `ValidationError`
- `AuthenticationError`
- `AuthorizationError`
- `NotFoundError`
- `BusinessRuleError`

Use the existing application exception handler and common response format.

Expected mapping:

|Exception|HTTP Status|
|---|---:|
|ValidationError|400|
|AuthenticationError|401|
|AuthorizationError|403|
|NotFoundError|404|
|BusinessRuleError|409|

Do not:

- catch all `Exception` inside each route
- expose stack traces
- expose SQL, database paths, or internal details
- replace existing safe messages with provider/database details
- add endpoint-specific incompatible error formats

---

# Testing Requirements

Add focused automated tests for this feature.

Use existing test organization and fixtures.

Expected test modules may include:

```text
backend/tests/api/test_projects.py
backend/tests/api/test_issues.py
```

Add or adjust focused Schema and Service tests only where behavior changes, such as `IssueListResponse`.

## Project API Tests

Test at minimum:

- authenticated Project list success
- exact response structure
- nested Hotel structure
- empty list
- unauthenticated request returns 401
- Service Dependency is called through the Router
- no Project write occurs

## Issue List API Tests

Test at minimum:

- authenticated success
- exact `items`, `page`, `page_size`, and `total` response
- empty result
- ROOM item shape
- OTHER item shape
- each approved filter is forwarded correctly
- combined filters are forwarded correctly
- pagination values are forwarded correctly
- updated-at ordering is preserved from the Service/Repository result
- Project not found returns 404
- unauthenticated request returns 401
- invalid approved query value follows the existing 400 flow when applicable

If defaults and bounds are approved and unambiguous, also test them exactly.

## Issue Detail API Tests

Test at minimum:

- authenticated success
- ROOM response
- OTHER response
- Project summary
- optional Room behavior
- creator and updater summaries
- Comment list
- Attachment list
- Issue not found returns 404
- unauthenticated request returns 401

## Create Issue API Tests

Test at minimum:

- ROOM success
- OTHER success
- authenticated user ID is passed to the Service
- exact response body
- initial Status is not accepted from the request
- invalid Target Type / Room / Target combination returns 400
- invalid Category returns 400
- empty Description returns 400
- Project not found returns 404
- unauthenticated request returns 401

## Update Issue API Tests

Test at minimum:

- ROOM success
- OTHER success
- authenticated user ID is passed to the Service
- exact response body
- invalid Target Type / Room / Target combination returns 400
- invalid Category returns 400
- empty Description returns 400
- Issue not found returns 404
- unauthenticated request returns 401

## Update Status API Tests

Test at minimum:

- each approved Status can be processed according to current Service behavior
- authenticated user ID is passed to the Service
- exact response body
- invalid Status returns 400
- Issue not found returns 404
- unauthenticated request returns 401

## Dependency Tests

Test Service construction only where it adds meaningful coverage:

- request-scoped Session is used
- correct existing Repositories are passed
- no database query runs in the Dependency itself

## Regression Tests

Run focused existing tests for:

- ProjectService
- IssueService
- ProjectRepository
- IssueRepository
- Project schemas
- Issue schemas
- authentication dependencies
- application creation and route registration

Then run the full test suite.

---

# Test Execution

Use the project's existing commands.

Typical commands:

```bash
cd backend
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/api/test_projects.py tests/api/test_issues.py
```

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/services/test_project_service.py tests/services/test_issue_service.py
```

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/repositories/test_project_repository.py tests/repositories/test_issue_repository.py
```

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

Also run:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
```

```bash
git diff --check
```

Use actual filenames present in the repository.

Do not claim a test passed unless it completed successfully.

If the Codex sandbox reproduces the known AnyIO `BlockingPortal` / Starlette `TestClient` hang:

1. confirm whether the failure occurs before entering the route
2. preserve the tests without skipping or weakening them
3. run them outside the affected sandbox when that execution mode is available
4. report the exact environment and result

Do not:

- increase timeouts and call that a fix
- delete tests
- mark tests `skip` or `xfail` merely because of the sandbox problem
- change production behavior to work around the sandbox

---

# Expected Files

Possible production files:

```text
backend/app/api/deps.py
backend/app/api/routes/__init__.py
backend/app/api/routes/projects.py
backend/app/api/routes/issues.py
backend/app/main.py
backend/app/schemas/issue.py
backend/app/services/issue_service.py
```

Possible test files:

```text
backend/tests/api/test_projects.py
backend/tests/api/test_issues.py
backend/tests/api/test_project_issue_dependencies.py
backend/tests/schemas/test_issue_schemas.py
backend/tests/services/test_issue_service.py
backend/tests/test_main.py
```

The exact modified-file set must be determined from the current implementation.

Do not modify every listed file automatically.

Modify only files necessary to satisfy the approved design and tests.

---

# Explicitly Out of Scope

Do not implement:

- AI Draft API
- Comment API
- Attachment API
- Attachment download behavior
- Frontend
- Project management API
- Hotel management API
- Room or RoomType management API
- User management API
- Administration API
- Issue deletion
- Comment update or deletion
- Attachment upload, list, download, or deletion
- JWT
- Bearer Tokens
- Refresh Tokens
- Server-side Session Database
- CSRF Token mechanism
- CORS redesign
- database schema changes
- SQLAlchemy Model changes
- Alembic migrations
- storage changes
- Ollama changes
- Docker
- unrelated dependency upgrades
- unrelated refactoring

Do not add undocumented response fields or endpoints.

---

# Dependency Policy

Do not add a new runtime dependency for this feature unless the approved implementation is impossible without it.

FastAPI, Pydantic, SQLAlchemy, and the current project dependencies are sufficient for this API integration.

Do not add:

- a pagination library
- a generic response framework
- another DI framework
- another ORM
- an API versioning framework

If a dependency appears necessary, stop and report before changing `pyproject.toml` or `uv.lock`.

---

# Documentation Policy

The user has already updated the approved Detailed Design for `IssueListResponse`.

Do not modify Requirements, Design Documents, ADRs, Project Conventions, or implementation guides unless explicitly instructed.

If implementation reveals a documentation conflict:

1. do not guess
2. do not silently alter the design
3. stop
4. report the exact conflicting files and sections
5. propose the minimum required design decision

Keep this implementation guide unchanged unless the user explicitly requests an update.

---

# Stop Conditions

Stop before implementation or immediately when discovered if any of the following applies.

## Design and Contract Ambiguity

- Pagination defaults or bounds are required but are not unambiguously defined by an approved source.
- Existing `IssueService.list_issues()` behavior conflicts with the new `IssueListResponse` contract.
- Existing Schema names or fields conflict with API Design.
- Successful HTTP status codes cannot be determined from existing project conventions without inventing behavior.
- The exact ownership of pagination validation cannot be resolved from approved design and current code.
- Project visibility or ownership filtering would need to be invented.
- API Design and Detailed Design disagree on a response field.
- Existing public DTOs would require an undocumented incompatible change.

## Architecture Conflict

- A Router would need to call a Repository directly.
- A Dependency would need to execute a database query.
- A Repository would need business validation or transaction ownership.
- A Service would need HTTP Request, Response, Cookie, or Session objects.
- The implementation would require a new architectural layer or framework.

## Scope Expansion

- A database Model or Migration change is required.
- A new database relationship is required.
- A new runtime dependency is required.
- An unrelated API must be implemented.
- Authentication design must change.
- Comment, Attachment, AI, or Frontend implementation becomes necessary.
- Unrelated failing tests would require code changes outside this feature.

## Existing-Code Conflict

- Current Service constructors or method signatures differ materially from the latest design.
- Existing routes already implement the endpoints with a conflicting contract.
- Current tests encode behavior that conflicts with the latest Source of Truth.
- User changes would need to be overwritten or discarded.

When stopping, do not partially “solve” the ambiguity by guessing.

Report:

- exact files and lines or sections
- the conflicting requirements
- why implementation cannot safely continue
- the minimum decision required

---

# Self-Review Requirements

After implementation, review all changes for:

- exact endpoint paths
- exact request and response shapes
- authentication on every endpoint
- correct authenticated User ID forwarding
- no Repository calls from Routers
- no SQLAlchemy queries in Routers or Dependencies
- no transaction handling outside Services
- no new undocumented behavior
- no unrelated file changes
- no database or migration changes
- no Frontend changes
- no added dependencies
- correct 400 / 401 / 404 behavior
- correct common error response format
- correct pagination response
- preservation of existing Authentication API behavior

Review the staged or unstaged diff, not only the files you intended to edit.

---

# Completion Report

At completion, report using exactly these headings.

## Summary

Summarize the implemented Project / Issue API behavior.

## Modified Files

List every modified and newly created file.

Separately identify files that existed as user changes before the task and were preserved unchanged.

## Tests

For every executed command, report:

- command
- result
- passed / failed / deselected counts
- timeout or environment limitations

Do not combine unexecuted tests with successful tests.

## Design Compliance

Confirm:

- endpoint contract compliance
- Layer responsibilities
- authentication integration
- transaction ownership
- no database or migration changes
- no unrelated changes

## Assumptions

List every implementation assumption.

If none:

```text
None.
```

## Remaining Work

List scope-excluded or unresolved work.

If none:

```text
None.
```

---

# Completion Criteria

This feature is complete only when:

- all six approved endpoints are implemented
- every endpoint requires the existing Session authentication
- Project list matches API Design
- Issue list returns `IssueListResponse`
- Issue detail matches API Design
- Create, update, and Status responses match API Design
- authenticated User ID reaches write Services
- Routers contain no business logic or database queries
- Services retain transaction ownership
- focused tests pass
- relevant regressions pass
- the full test suite is executed or an exact environment limitation is documented
- `git diff --check` passes
- no Stop Condition remains unresolved
