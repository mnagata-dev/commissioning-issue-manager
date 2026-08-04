# AI Draft API Integration Implementation Guide

## Purpose

Implement the authenticated AI Draft API for CIM by connecting the existing `AIService`, Ollama Client, repositories, schemas, authentication, and common error handling to the approved API contract.

Store this file as:

```text
docs/implementation/feature-ai-draft-api.md
```

---

# Scope

Implement:

```http
POST /api/ai/issue-draft
```

Include:

- AI Router
- `AIService` dependency construction
- Router registration
- existing Session authentication
- forwarding authenticated `user_id`
- API, dependency, and route-registration tests
- relevant regression tests

Reuse the existing AI foundation. Do not redesign it.

---

# Source of Truth

Before editing, read the latest:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/project_conventions.md`
- `docs/requirements/requirements.md`
- `docs/design/basic_design.md`
- `docs/design/database_design.md`
- `docs/design/api_design.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/adr/ADR-001-user-in-control.md`
- `docs/adr/ADR-002-target-type-definition.md`
- `docs/adr/ADR-003-category-definition.md`

Inspect the current implementation:

- `backend/app/api/deps.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/clients/ollama_client.py`
- `backend/app/repositories/project_repository.py`
- `backend/app/repositories/room_repository.py`
- `backend/app/schemas/ai.py`
- `backend/app/services/ai_service.py`
- `backend/tests/services/test_ai_service.py`
- `backend/tests/clients/test_ollama_client.py`
- existing API, dependency, configuration, and route tests

Follow the actual repository structure if paths differ. Do not create duplicate implementations.

---

# Branch and Git Rules

Work only on:

```text
feature/ai-draft-api
```

Before editing:

```bash
git branch --show-current
git status --short
```

Do not:

- switch or create branches
- commit
- push
- create a Pull Request
- merge
- rewrite history
- modify unrelated files
- overwrite user changes

Preserve:

- `docs/design/api_design.md`
- `docs/implementation/feature-ai-draft-api.md`

---

# Approved API Contract

## Endpoint

```http
POST /api/ai/issue-draft
```

## Authentication

Use the existing Cookie-based Session authentication.

Allowed roles:

- `ADMINISTRATOR`
- `ENGINEER`

Unauthenticated requests return `401`.

## Request

Reuse `GenerateDraftRequest` unchanged:

```python
project_id: int
target_type: str
room_id: int | None
target: str | None
input_text: str
```

ROOM example:

```json
{
  "project_id": 1,
  "target_type": "ROOM",
  "room_id": 1,
  "target": null,
  "input_text": "Bathroom light does not turn off."
}
```

OTHER example:

```json
{
  "project_id": 1,
  "target_type": "OTHER",
  "room_id": null,
  "target": "Network",
  "input_text": "Processor cannot communicate with gateway."
}
```

Do not add request fields.

## Response

Reuse `GenerateDraftResponse` unchanged:

```python
category: str
description: str
```

Example:

```json
{
  "category": "LIGHTING",
  "description": "Bathroom light remains on after operation."
}
```

Return only `category` and `description`.

Do not return Room, Target Type, Target, Project, model metadata, prompt, raw provider output, timing, tokens, or persisted IDs.

## Errors

|Condition|HTTP status|
|---|---|
|Invalid input or business validation|400|
|Unauthenticated|401|
|Project missing|404|
|Room missing|404|
|AI/Ollama failure|500|

Use the existing common error response.

Do not expose Ollama host, model configuration, prompts, raw responses, internal exceptions, SQLAlchemy details, or stack traces.

---

# User in Control

AI generates only:

- Category
- Description

AI must not:

- decide Room
- decide Target Type
- decide Target
- save or update Issue
- update Status
- add Comment
- add Attachment
- change Master Data

The endpoint returns a Draft only. Final confirmation and Issue registration remain the user's responsibility.

---

# Architecture

```text
HTTP Request
    │
    ▼
AI Router
    │
    ▼
AIService
    ├── ProjectRepository
    ├── RoomRepository
    └── OllamaClient
```

## Router Responsibilities

The Router may:

- receive `GenerateDraftRequest`
- receive authenticated User through dependency injection
- call `AIService.generate_issue_draft()`
- return `GenerateDraftResponse`

The Router must not:

- query the database
- call repositories
- call Ollama directly
- build prompts
- validate Project or Room
- implement Target Type rules
- validate AI output
- manage transactions
- access Session manually
- persist business data

## AIService Responsibilities

Reuse:

```python
generate_issue_draft(
    request: GenerateDraftRequest,
    user_id: int,
) -> GenerateDraftResponse
```

AIService owns:

- Project existence validation
- Target Type validation
- Room/Target consistency validation
- Room existence validation
- Room and Project Hotel consistency validation
- `input_text` validation
- Ollama Client invocation
- AI output validation
- conversion to `GenerateDraftResponse`
- conversion of provider failures to `AIServiceError`

AIService must not:

- save Draft or Issue
- commit, rollback, flush, or add entities
- authenticate or authorize
- re-fetch User
- use User data in the prompt
- expose provider objects to the Router

`user_id` is forwarded from the API but is not used for prompting or personalization.

## Ollama Client Responsibilities

Reuse the current implementation and approved behavior:

- official `ollama` Python Client
- synchronous `Client`
- `chat()`
- streaming disabled
- temperature `0`
- Structured Output using JSON Schema
- configured host, model, and timeout

Do not add streaming, retries, fallback models, another provider, generic provider abstractions, conversation history, or persistence.

## Repository Responsibilities

Repositories remain data-access-only.

Do not add AI logic, prompt logic, validation, transaction management, or HTTP concerns.

---

# Validation Rules

## Project

`project_id` must exist.

Missing Project:

```text
NotFoundError → 404
```

## Target Type

Allowed values:

```text
ROOM
OTHER
```

Undefined values:

```text
ValidationError → 400
```

Do not normalize case or replace values.

## ROOM

For `ROOM`:

- `room_id` is required
- `target` must be `None`
- Room must exist
- Room must belong to the same Hotel as Project

Missing Room returns `404`.

Invalid combinations use the existing approved validation/business-rule behavior.

AI must not infer or replace Room.

## OTHER

For `OTHER`:

- `room_id` must be `None`
- `target` is required

AI must not infer or replace Target.

## Input Text

`input_text` must not be empty.

Do not trim, translate, normalize, supplement, or invent length limits unless already implemented and documented.

Empty input returns `400`.

## AI Output

Output must contain valid:

```python
category
description
```

Category must be a defined Category.

Description must exist, be a string, and not be empty.

Invalid output returns:

```text
AIServiceError → 500
```

Do not convert invalid Category values to `OTHER`.

---

# Prompt Policy

Preserve the existing approved prompt.

System Message must enforce:

- CIM Issue Draft assistance
- Category and Description only
- defined Category values only
- natural Issue Description
- no invented facts
- no Target Type, Room, or Target output
- no persistence
- `OTHER` only when the AI cannot determine Category

User Message context includes:

- selected Target Type
- Room Number for ROOM
- selected Target for OTHER
- `input_text`

Do not include:

- `project_id`
- `user_id`
- Username
- Role
- Session data
- model configuration

Do not modify prompt behavior merely for API integration.

---

# Configuration

Reuse:

|Setting|Environment variable|Default|
|---|---|---|
|Host|`CIM_OLLAMA_HOST`|`http://localhost:11434`|
|Model|`CIM_OLLAMA_MODEL`|none|
|Timeout|`CIM_OLLAMA_TIMEOUT_SECONDS`|`60`|

The application must start without `CIM_OLLAMA_MODEL`.

Calling the AI endpoint without a configured model returns `AIServiceError` through common `500` handling.

Do not hard-code a model or change configuration names/defaults.

---

# Dependency Construction

Add or extend:

```python
get_ai_service(...)
AIServiceDependency
```

Construct the existing `AIService` using the request-scoped Session, current repository constructors, current Ollama Client constructor, and current settings.

Dependency functions must not:

- query the database
- call Ollama
- perform validation
- create another Session
- introduce another DI framework

---

# Router Integration

Use:

```text
backend/app/api/routes/ai.py
```

Expected flow:

```python
result = ai_service.generate_issue_draft(
    request=request,
    user_id=current_user.id,
)
return result
```

Register through:

- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`

OpenAPI must contain exactly one `POST` operation for:

```text
/api/ai/issue-draft
```

---

# Error Handling

Use existing project exceptions and handlers.

|Condition|Expected behavior|
|---|---|
|Request parsing failure|common safe 400|
|Business validation failure|`ValidationError` → 400|
|Unauthenticated|`AuthenticationError` → 401|
|Project missing|`NotFoundError` → 404|
|Room missing|`NotFoundError` → 404|
|Connection failure|`AIServiceError` → 500|
|Timeout|`AIServiceError` → 500|
|Provider error|`AIServiceError` → 500|
|Model missing at use time|`AIServiceError` → 500|
|Invalid Structured Output|`AIServiceError` → 500|
|Invalid Category|`AIServiceError` → 500|
|Missing/invalid/empty Description|`AIServiceError` → 500|

Do not add endpoint-local broad `try/except` blocks.

---

# Persistence and Transactions

AI Draft generation is read-only.

Do not:

- create Draft records
- create or update Issue
- write AI history
- commit
- rollback
- flush
- add SQLAlchemy entities

---

# Schema Policy

Reuse unchanged:

```python
GenerateDraftRequest
GenerateDraftResponse
```

Do not add metadata, confidence, explanations, model name, prompt, raw output, Target information, or persistent IDs.

---

# Out of Scope

Do not implement:

- speech recognition
- audio upload
- microphone integration
- Frontend
- AI chat
- conversation memory
- prompt history
- AI execution history
- Issue auto-save
- Room/Target/Target Type inference
- model-selection API or UI
- retries
- fallback models
- streaming
- async Ollama migration
- background jobs
- caching
- metrics
- token accounting
- confidence scores
- another AI provider
- database or migration changes
- Authentication changes
- unrelated refactoring
- dependency upgrades

---

# Dependency Policy

Use existing dependencies.

If a new runtime dependency appears necessary:

1. stop
2. do not change `backend/pyproject.toml`
3. do not change `backend/uv.lock`
4. report the reason
5. wait for approval

---

# Documentation Policy

Preserve the user changes in:

- `docs/design/api_design.md`
- `docs/implementation/feature-ai-draft-api.md`

Do not modify other requirements, design documents, ADRs, conventions, or implementation guides unless explicitly instructed.

If a documentation conflict appears, stop and report exact files and sections.

---

# Tests

## API Tests

Cover at minimum:

### Authentication

- unauthenticated request returns `401`

### Success

- valid ROOM request returns exact response
- valid OTHER request returns exact response
- Router forwards request DTO unchanged
- Router forwards `current_user.id`
- no extra response fields

### Validation

- malformed body returns common safe `400`
- missing fields return `400`
- invalid field types return `400`
- invalid Target Type returns `400`
- invalid ROOM combination returns `400`
- invalid OTHER combination returns `400`
- empty `input_text` returns `400`
- Service is not called when request parsing fails

### Not Found

- missing Project returns `404`
- missing Room returns `404`

### AI Failure

- model missing returns common `500`
- connection failure returns common `500`
- timeout returns common `500`
- invalid Structured Output returns common `500`
- invalid Category returns common `500`
- missing/empty Description returns common `500`
- internal details are not exposed

Use dependency overrides and mocks. Do not require a running Ollama server.

## Dependency Tests

Verify:

- `get_ai_service()` constructs current dependencies
- request-scoped Session is used
- no DB query occurs during construction
- no Ollama request occurs during construction

## Route Tests

Verify:

- path is registered
- only `POST` is registered
- no duplicate operation
- existing routes remain registered

## Existing AI Tests

Run existing AIService and Ollama Client tests. Do not rewrite them unless a genuine approved integration issue requires it.

Do not weaken, delete, skip, or xfail tests.

---

# Required Verification

From `backend/`:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q   tests/api/test_ai.py   tests/services/test_ai_service.py   tests/clients/test_ollama_client.py   tests/api/test_project_issue_dependencies.py   tests/test_main.py
```

Adjust paths only if the actual repository differs.

Run the full suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q
```

Run:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
```

From repository root:

```bash
git diff --check
```

Report exact commands and results. Collection-only is not execution success.

If the known TestClient/AnyIO sandbox issue occurs, verify it is the same limitation and run outside the normal sandbox when permitted.

---

# Stop Conditions

Stop immediately if:

## Branch or Working Tree

- current branch is not `feature/ai-draft-api`
- user changes would need to be overwritten

## Design Conflict

- Requirements, API Design, Detailed Design, Test Design, or User in Control conflict
- request/response fields differ
- Project/Room 404 behavior is unclear
- Project/Room Hotel mismatch behavior cannot be determined
- `user_id` use is ambiguous
- input validation requires inventing rules
- Category definitions conflict
- AI output validation conflicts
- model-missing behavior conflicts
- response would require fields beyond Category and Description

## Architecture Conflict

- Router must call Repository or Ollama
- Dependency must query DB or call Ollama
- Repository needs AI logic
- Ollama Client needs business validation
- AIService needs HTTP/Session objects
- a new architecture/framework is required

## Existing-Code Conflict

- current AIService materially conflicts with Detailed Design
- current Ollama Client materially conflicts with approved design
- current schemas conflict with API Design
- common handlers cannot express 400/401/404/500
- existing tests conflict with Source of Truth
- integration requires redesigning AI behavior

## Scope Expansion

- new runtime dependency required
- database/Model/Migration change required
- Authentication or Frontend change required
- another API feature must change
- public DTO change required
- provider upgrade required
- unrelated test failures require unrelated changes

When stopping, report exact files/sections, conflict, minimum decision, files changed, and tests run. Do not guess.

---

# Self-Review

Confirm:

- exact endpoint/method
- existing Session authentication
- `current_user.id` forwarded
- Router calls AIService only
- no DB query or Ollama call in Router/Dependency
- schemas unchanged
- response contains only Category and Description
- Project/Room missing returns `404`
- validation returns common `400`
- AI failures return common `500`
- no internal provider details exposed
- no business data persisted
- no transaction added
- User and Project ID absent from prompt
- AI does not determine Room, Target Type, or Target
- no model hard-coding
- no new dependencies
- no DB, Model, Migration, Frontend, Comment, Attachment, or unrelated changes
- user documentation changes preserved

---

# Completion Report

Use exactly:

## Summary

## Modified Files

## Tests

## Design Compliance

## Assumptions

Use:

```text
None.
```

when there are none.

## Remaining Work

Use:

```text
None.
```

when there is none.

---

# Completion Criteria

Complete only when:

- endpoint is implemented and authenticated
- authenticated User ID is forwarded
- request/response exactly match the contract
- ROOM and OTHER succeed
- Project/Room missing return `404`
- validation returns `400`
- AI failures return `500`
- response contains only Category and Description
- no persistence or transaction occurs
- Router has no business logic, DB query, or Ollama call
- existing AIService/Ollama foundation is reused
- focused and full tests complete
- compile verification passes
- `git diff --check` passes
- no Stop Condition remains
