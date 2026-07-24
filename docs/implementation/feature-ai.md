# AI Foundation Implementation Guide

## Feature

`feature/ai`

---

## Purpose

Implement the AI Draft foundation for the Commissioning Issue Manager (CIM).

This feature implements the application-side AI Draft flow that uses Ollama to generate only:

- `category`
- `description`

from user-provided Issue input.

The AI is an input-assistance mechanism only. It must not decide or persist the final Issue.

This file is the Codex implementation instruction for this feature and must be stored as:

```text
docs/implementation/feature-ai.md
```

The implementation must follow the current design documents and existing code. Do not invent an Ollama transport, model name, endpoint, timeout, prompt format, parsing strategy, retry policy, or dependency when those details are not already defined.

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
- `docs/implementation/feature-schemas.md`
- `docs/implementation/feature-services.md`
- `docs/implementation/feature-auth.md`

Follow the source-of-truth priority defined in `AGENTS.md`.

Inspect the current implementation before editing, especially:

- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/schemas/ai.py`
- `backend/app/schemas/issue.py`
- `backend/app/models/enums.py`
- `backend/app/repositories/project_repository.py`
- `backend/app/repositories/room_repository.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/services/`
- project dependency files
- any existing Ollama or AI-related modules/tests

Do not assume an attached copy is newer than the repository version.

If the current design, configuration, dependency set, or existing implementation does not define enough information to implement the Ollama integration without guessing, apply the Stop Conditions below.

Do not modify design documents in this feature unless the user has already made and staged a design clarification before implementation begins.

---

# Current Design Contract

The current design establishes the following AI behavior:

- Ollama is the AI provider for the initial version.
- AI Draft is input assistance only.
- AI generates:
  - `category`
  - `description`
- AI does not generate or infer:
  - Target Type
  - Room
  - Target
- AI does not save an Issue.
- The user reviews and decides whether to register the generated Draft.
- When AI processing fails, manual Issue entry must remain possible.
- AI failures use `AIServiceError`.
- AI-related database persistence is not required.

The current request schema is conceptually:

```python
GenerateDraftRequest(
    project_id: int,
    target_type: str,
    room_id: int | None,
    target: str | None,
    input_text: str,
)
```

The current response schema is:

```python
GenerateDraftResponse(
    category: str,
    description: str,
)
```

The detailed design defines the conceptual Service method:

```python
generate_issue_draft(
    request: GenerateDraftRequest,
    user_id: int,
) -> GenerateDraftResponse
```

Do not change this public Service contract unless the current repository version of the approved design explicitly differs.

---

# Scope

Implement only the AI Draft foundation that is fully supported by the approved design and existing project configuration.

Expected implementation areas are:

- Add the official `ollama` Python package as a project dependency
- Add Ollama configuration to `app/core/config.py`
- Add `app/clients/__init__.py`
- Add `app/clients/ollama_client.py`
- Implement `AIService`
- Update Service package exports where necessary
- Add focused AIService tests
- Add focused Ollama Client tests
- Add minimal provider test doubles or fixtures

Use the official `ollama` Python Client.

Do not introduce `requests`, LangChain, LlamaIndex, or another AI framework for this feature.

Follow the existing project dependency version convention and let `uv` record the resolved version in `uv.lock`.

---

# Out of Scope

Do not implement in this feature:

- AI API routes
- FastAPI dependencies
- Issue creation or update
- automatic saving of AI-generated data
- automatic selection of Target Type
- automatic Room selection
- automatic Target generation
- attachment analysis
- image recognition
- speech-to-text
- audio processing
- prompt-management UI
- prompt history
- conversation memory
- streaming responses
- background jobs
- retry queues
- model downloading or installation
- Ollama process management
- authentication or authorization
- database schema changes
- Alembic migrations
- Repository redesign
- Schema redesign
- Frontend changes
- unrelated refactoring

Do not add a generic AI framework or provider abstraction solely for hypothetical future providers.

---

# Responsibility Boundary

## AIService

`AIService` owns application-level AI Draft behavior.

Responsibilities include only behavior defined by the current design:

- validating application-level inputs that must be checked before calling AI
- building or delegating construction of the AI request/prompt according to the approved prompt design
- invoking the Ollama integration boundary
- validating the AI result
- converting the result to `GenerateDraftResponse`
- converting provider failures to `AIServiceError`

`AIService` must not:

- persist Issue data
- call IssueRepository to create or update an Issue
- commit or roll back a database transaction
- infer Target Type
- infer Room
- infer Target
- override user-selected Target information
- silently replace invalid AI output with invented business data

---

## Ollama Integration Boundary

Implement a dedicated Ollama integration module:

```text
app/clients/ollama_client.py
```

Use the official synchronous `ollama.Client`.

The Ollama Client owns:

- endpoint communication
- `chat()` invocation
- request serialization
- provider response extraction
- connection / timeout / provider error detection

The Ollama Client must not own:

- Project validation
- Room validation
- Target Type validation
- Category business validation
- Issue persistence
- API response formatting

`AIService` owns CIM business validation and AI Draft result validation.

Do not create a generic AI Provider hierarchy in this feature.

---

# Dependencies and Configuration

Add the official `ollama` Python package to the project dependencies.

Do not add another HTTP or AI framework for this feature.

Add the following Settings values to `app/core/config.py` using the existing Settings convention:

| Setting | Environment Variable | Default |
|---|---|---|
| Ollama host | `CIM_OLLAMA_HOST` | `http://localhost:11434` |
| Ollama model | `CIM_OLLAMA_MODEL` | `None` |
| Ollama timeout | `CIM_OLLAMA_TIMEOUT_SECONDS` | `60` |

The Model must not be hard-coded in application code.

The application must remain able to start when `CIM_OLLAMA_MODEL` is not configured.

When AI Draft generation is requested without a configured Model, raise `AIServiceError`.

Create the official synchronous Ollama Client using the configured host and timeout.

Do not manage the Ollama process or download models from the application.

---

# `AIService.generate_issue_draft()`

Expected signature:

```python
generate_issue_draft(
    request: GenerateDraftRequest,
    user_id: int,
) -> GenerateDraftResponse
```

Use the current implemented schema classes.

The `user_id` parameter does not cause User lookup, authorization, or personalization in this feature.

Do not include User information in the AI prompt.

---

# Input Rules

## Project

Retrieve the Project through `ProjectRepository.find_by_id(request.project_id)`.

If the Project does not exist, raise `NotFoundError`.

Do not include `project_id` or Project metadata in the AI prompt.

## Target Type / Room / Target

Validate the same Target consistency rules used for Issue input.

Only these Target Types are allowed:

```text
ROOM
OTHER
```

For `ROOM`:

- `room_id` is required
- `target` must be `None`
- retrieve the Room using `RoomRepository.find_by_id()`
- missing Room raises `NotFoundError`
- the Room must belong to the same Hotel as the Project
- Hotel mismatch raises `ValidationError`

For `OTHER`:

- `room_id` must be `None`
- `target` is required
- `target` must not be the empty string

Invalid combinations raise `ValidationError`.

Do not trim or normalize `target`.

The validated Target context may be supplied to the AI only as context.

The AI must not generate, replace, or return Target Type, Room, or Target.

## Input Text

`input_text` must not be the empty string.

Empty input raises `ValidationError`.

Do not trim, translate, truncate, normalize, replace, or enrich `input_text`.

---

# Prompt Policy

Construct two messages:

- System Message
- User Message

The System Message must instruct the model that:

- it assists CIM Issue Draft creation
- output is limited to `category` and `description`
- Category must be one of the existing CIM Category values
- Description must be based only on the user's input
- missing commissioning facts must not be invented
- Target Type, Room, and Target must not be inferred or changed
- the AI must not save or register an Issue
- when Category cannot be determined, return `OTHER`

The User Message must contain:

- selected Target Type
- Room Number when Target Type is `ROOM`
- selected Target when Target Type is `OTHER`
- `input_text`

Do not include:

- `project_id`
- User information
- database IDs other than information required to express the already-selected target context

Target information is context only and must not appear as additional response fields.

---

# AI Result Validation

Define a private/internal Pydantic model for Ollama Structured Output.

It must contain only:

```python
category: Category
description: str
```

Reject extra fields.

Description must not be empty.

Use the existing `Category` enum as the allowed-value source.

The following conditions raise `AIServiceError`:

- malformed JSON
- response does not match the Structured Output schema
- missing Category
- unsupported Category
- missing Description
- non-string Description
- empty Description
- unexpected additional output fields

Do not coerce an invalid Category to `OTHER`.

`OTHER` is used only when the model follows the Prompt instruction and explicitly returns it.

---

# Provider Response Format

Use Ollama Structured Outputs.

Call the official Ollama Client `chat()` method with:

- `stream=False`
- `format=<internal Pydantic model>.model_json_schema()`
- `options={"temperature": 0}`

The provider response is read from the assistant Message Content.

Validate that content using the internal Pydantic model.

Convert the successfully validated result into:

```python
GenerateDraftResponse(
    category=<category value as string>,
    description=<description>,
)
```

Do not implement free-text parsing such as `Category:` or `Description:` label extraction.

---

# Error Handling

Use the existing `AIServiceError` for AI/provider processing failures.

Convert the following to `AIServiceError`:

- Ollama connection failure
- Ollama timeout
- Ollama provider error response
- Model not configured
- malformed Structured Output
- invalid Category
- missing or invalid Description

The Ollama integration boundary may inspect provider-specific exceptions, but `AIService` must not expose them outside the Service boundary.

Do not expose:

- Ollama endpoint
- raw provider exception
- Prompt
- provider payload
- stack trace

in the public error message.

Unexpected programming errors that are unrelated to provider communication or response validation must not be silently converted into `AIServiceError`.

---

# Transaction Policy

AI Draft generation is read-only with respect to CIM business data.

Therefore:

- do not call `session.commit()`
- do not call `session.rollback()`
- do not create or mutate Issue entities
- do not call Repository create/update methods
- do not add database persistence for prompts or responses
- do not inject a SQLAlchemy `Session` merely because other Services use one

---

# User in Control

The generated result is a Draft only.

Preserve this flow:

```text
User input
    ↓
AI Draft generation
    ↓
GenerateDraftResponse
    ↓
User reviews/edits
    ↓
Separate Issue registration flow
```

Never implement automatic Issue registration from AI output.

---

# Tests

Use unit tests.

Tests must not require:

- a running Ollama server
- a real network connection
- a real AI model
- a real SQLite database
- FastAPI `TestClient`

Mock or fake the provider boundary.

Use the real schemas and Category enum where practical.

Do not make tests depend on nondeterministic model output.

## AIService Tests

When design is sufficient, cover at minimum:

- successful Draft generation
- response contains only `category` and `description`
- Target Type is not generated or replaced
- Room is not generated
- Target is not generated
- AI result is not persisted
- no commit occurs
- valid Category is accepted
- provider failure becomes `AIServiceError`
- malformed provider response follows approved behavior
- invalid Category follows approved behavior
- Repository lookups occur only when explicitly required by design

## Provider Client Tests

If a separate Ollama client is implemented, use mocked transport tests only.

Cover only the approved contract:

- configured endpoint/model is used
- expected request structure is sent
- valid response is extracted
- transport failures follow the approved error boundary

## Prompt Tests

Verify only required semantic constraints, including:

- Category restricted to defined values
- output limited to Category and Description
- no Target Type inference
- no Room inference
- no Target inference
- no automatic Issue persistence
- undetermined Category should be `OTHER`

Do not assert a large prompt byte-for-byte unless the project convention requires it.

---

# Required Verification

Run from `backend/`.

Run focused AI tests using actual paths created by this feature, for example:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/services/test_ai_service.py
```

If a separate provider client is implemented:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/ai
```

Then:

```bash
git diff --check
```

Then attempt:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

If the full suite encounters the known timeout in `test_application_error_uses_common_response`:

- report the timeout accurately
- confirm focused AI tests passed independently
- do not modify the unrelated exception-handler test
- do not claim the full suite passed

---

# Completion Report

When implementation is complete, report:

## Summary

- AIService implementation status
- Ollama integration implementation status
- tests added

## Modified Files

List every modified and new file.

## AI Service Methods

List implemented public methods.

## Ollama Integration

Report:

- integration boundary/module
- client or transport dependency used
- configuration values used
- provider response format used

Do not include machine secrets or sensitive local configuration values.

## Prompt Behavior

Summarize:

- inputs supplied to AI
- output fields requested
- Category constraints
- Target Type / Room / Target non-inference rule
- fallback instruction for undetermined Category

## Validation Behavior

Summarize:

- request validation performed by the Service
- AI result validation
- invalid Category behavior
- malformed output behavior

## Error Behavior

Summarize:

- provider failure mapping
- malformed response mapping
- public exception/message behavior

## Transaction Behavior

Confirm:

- no business-data commits
- no Issue persistence
- no automatic registration
- no unnecessary SQLAlchemy Session

## Tests

Report every command and exact result.

## Design Compliance

Confirm:

- no API routes added
- no database changes
- no Repository redesign
- no Schema redesign
- no AI-generated Target Type, Room, or Target
- no automatic Issue persistence
- no unrelated refactoring

## Issues or Ambiguities

List unresolved issues. If none remain, state that none remain.

## Remaining Work

State remaining work such as:

- AI API integration
- Attachment/Storage
- API authentication integration
- remaining API Layer work

---

# Stop Conditions

Stop and report before continuing if any of the following is found:

- The official `ollama` Python Client cannot support the approved `chat()` and Structured Output contract.
- The existing Settings implementation cannot represent the approved Ollama configuration without a broader configuration redesign.
- The installed Ollama version or selected local model cannot support the required Structured Output behavior.
- `AIServiceError` construction or public error behavior is ambiguous.
- Implementing AI requires changing existing public request or response DTOs.
- Implementing AI requires a database model or migration change.
- Implementing AI requires Issue persistence.
- Existing code already implements the AI/Ollama boundary differently from the latest design.
- Implementing the feature would require adding HTTP/API-specific behavior to `AIService`.
- An unrelated test failure would require changing code outside this feature.

Do not resolve Ollama, prompt, parsing, validation, or provider decisions by guessing.
