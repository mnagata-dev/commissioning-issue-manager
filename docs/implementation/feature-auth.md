# Authentication Foundation Implementation Guide

## Feature

`feature/auth`

---

## Purpose

Implement the authentication foundation for the Commissioning Issue Manager (CIM).

This feature is responsible for password verification, authentication-oriented Service logic, and the reusable security utility required by the later API authentication flow.

This file is the Codex implementation instruction for this feature and must be stored as:

```text
docs/implementation/feature-auth.md
```

The implementation must follow the current design documents and existing code. Do not invent an authentication transport, password hashing algorithm, token format, cookie policy, or session-storage mechanism that has not already been defined.

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

Follow the source-of-truth priority defined in `AGENTS.md`.

Inspect the current implementation before editing, especially:

- `backend/app/core/security.py`
- `backend/app/core/exceptions.py`
- `backend/app/models/user.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/`
- project dependency files
- existing authentication-related tests, if any

Do not assume an attached document is newer than the repository version.

If the design documents, dependencies, or existing implementation do not define enough information to implement authentication safely and consistently, apply the Stop Conditions below. Do not guess.

Do not modify design documents unless the user has already made and staged a design clarification before this implementation begins.

---

# Current Design Contract

The current design establishes the following:

- Users authenticate with:
  - `username`
  - `password`
- `username` is the login ID.
- Email-address format is permitted for `username`.
- The User model stores:
  - `username`
  - `password_hash`
  - `display_name`
  - `role`
- Plain-text passwords must not be stored in the database.
- `UserRepository.find_by_username(username)` is the data-access boundary for login lookup.
- `CurrentUserResponse` contains:
  - `id`
  - `username`
  - `display_name`
  - `role`
- Authentication failures map to `AuthenticationError`.
- Unauthenticated API access eventually maps to HTTP `401`.
- API authentication endpoints are defined as:
  - `POST /api/auth/login`
  - `POST /api/auth/logout`
  - `GET /api/auth/me`
- API Router and FastAPI dependency implementation are not part of this feature unless explicitly stated below.

The design currently defines these AuthService methods:

```python
login(username: str, password: str) -> CurrentUserResponse

get_current_user(user_id: int) -> CurrentUserResponse
```

Authentication state handling and logout behavior are not defined in AuthService at this stage.

Do not infer how authenticated user identity is transported between HTTP requests. That belongs to the later API authentication integration design.

---

# Scope

Implement only the authentication foundation that is fully supported by the current design and existing project dependencies.

Expected implementation areas are:

- Add the `pwdlib[argon2]` project dependency
- Password security utility in `app/core/security.py`
- `AuthService`
- Authentication foundation unit tests
- Service package export update where necessary

The intended AuthService responsibilities are:

- Look up a User by username.
- Verify a submitted password against `password_hash`.
- Return `CurrentUserResponse` after successful credential verification.
- Retrieve a current User by an already-resolved authenticated `user_id`.
- Avoid exposing whether a username exists through login error messages.

`logout()` is not implemented in this feature.

Authentication state handling and logout behavior will be defined in a later API authentication integration feature.

---

# Out of Scope

Do not implement in this feature:

- Authentication API routes
- FastAPI authentication dependencies
- Cookie creation or deletion
- HTTP session middleware
- Server-side session storage
- JWT generation or verification
- Bearer-token authentication
- Refresh Tokens
- CSRF protection
- Authorization dependencies
- Role-based endpoint restrictions
- User creation CLI
- Password reset/change flows
- Account lockout
- Rate limiting
- MFA
- Database schema changes
- Alembic migrations
- UserRepository redesign
- Schema redesign
- Frontend login UI
- AI, Attachment, or Storage functionality
- Unrelated refactoring

Adding `pwdlib[argon2]` for password hashing and verification is explicitly approved for this feature.

Do not install or introduce any additional authentication framework or authentication-state library merely to complete this feature.

Do not add authentication state to the User table unless explicitly required by an approved design change.

---

# Expected Directory Structure

Follow the existing project structure.

Expected additions or modifications:

```text
backend/
├── app/
│   ├── core/
│   │   └── security.py
│   └── services/
│       ├── __init__.py
│       └── auth_service.py
└── tests/
    ├── core/
    │   └── test_security.py
    └── services/
        └── test_auth_service.py
```

If the repository already has an established test location for core utilities, use that convention instead.

Do not create empty placeholder files.

---

# Password Security Utility

## Responsibility

`app/core/security.py` owns password hashing and password verification primitives.

The Service Layer must not know the hashing implementation details.

Expected conceptual interface:

```python
hash_password(password: str) -> str

verify_password(password: str, password_hash: str) -> bool
```

`verify_password()` is required by `AuthService.login()`.

`hash_password()` should be implemented only when the same configured password-hashing mechanism can be used safely and is required for future user provisioning.

---

## Password Algorithm Rule

Use the password hashing mechanism defined by the current detailed design:

- Library: `pwdlib`
- Argon2 support: enabled through `pwdlib[argon2]`
- Configuration: `PasswordHash.recommended()`

Add `pwdlib[argon2]` to the project dependencies if it is not already present.

Use `PasswordHash.recommended()` for password hashing and verification.

Do not hard-code Argon2 parameters in the application.
Use the configuration selected by `PasswordHash.recommended()`.

Do not introduce another password hashing mechanism such as:

- bcrypt
- PBKDF2
- scrypt
- Passlib
- framework-specific password helpers

Do not use:

- plain SHA hashes
- MD5
- reversible encryption
- custom password hashing
- plain-text comparison

Do not expose password values or password hashes in errors or logs.

---

# AuthService

## Dependencies

Use only:

- `UserRepository`
- password verification function from `app.core.security`

Do not inject SQLAlchemy `Session` unless the approved implementation actually performs a transactional write. Authentication credential verification is read-only.

Do not query SQLAlchemy directly.

---

## `login()`

Expected signature:

```python
login(username: str, password: str) -> CurrentUserResponse
```

Requirements:

1. Retrieve the User using:

```python
UserRepository.find_by_username(username)
```

2. If no User exists, raise `AuthenticationError`.

3. Verify the submitted password against `user.password_hash` using the security utility.

4. If password verification fails, raise the same `AuthenticationError` used for an unknown username.

5. Do not reveal whether:
   - the username does not exist, or
   - the password is incorrect.

6. On success, return:

```python
CurrentUserResponse(
    id=user.id,
    username=user.username,
    display_name=user.display_name,
    role=user.role.value,
)
```

Use the actual existing Role representation when converting to the API-facing string.

7. Do not:
   - commit
   - rollback
   - mutate the User
   - issue a token
   - create a cookie
   - create a session
   - return `password_hash`

Use a stable generic authentication error message such as the existing project convention requires.

If the existing `AuthenticationError` constructor or error-code convention is unclear, inspect current exception tests and handlers. If it remains ambiguous, stop.

---

## `get_current_user()`

Expected signature:

```python
get_current_user(user_id: int) -> CurrentUserResponse
```

This method assumes that a later API authentication mechanism has already resolved an authenticated `user_id`.

Requirements:

1. Retrieve the User using:

```python
UserRepository.find_by_id(user_id)
```

2. If the User cannot be found, treat the authenticated identity as invalid and raise `AuthenticationError`.

3. Return `CurrentUserResponse`.

4. Do not:
   - commit
   - mutate the User
   - perform role authorization
   - inspect cookies, headers, or tokens

Do not implement the mechanism that produces `user_id` in this feature.

---

# Logout

Do not implement `AuthService.logout()` in this feature.

The current detailed design intentionally leaves authentication-state handling and logout behavior to a later API authentication integration design.

Do not introduce:

- Cookie-based authentication
- Server-side Session
- JWT
- Access Token
- Refresh Token
- Token revocation

Do not add a no-op `logout()` method.

Logout behavior will be defined after the authentication transport/state mechanism is selected.

---

# Authorization Boundary

Authentication and authorization are separate concerns.

This feature must not implement endpoint authorization.

Do not add:

- `require_administrator()`
- role checks inside `AuthService.login()`
- role checks inside `get_current_user()`
- Project-level access checks
- Issue-level access checks

The current roles remain:

```text
ADMINISTRATOR
ENGINEER
```

`CurrentUserResponse.role` remains a string.

Authorization dependencies belong to a later API/auth integration feature unless explicitly approved otherwise.

---

# Error Handling

Use existing custom exceptions.

Expected authentication exception:

```python
AuthenticationError
```

Credential failure must not use:

- `ValidationError`
- `NotFoundError`
- FastAPI `HTTPException`

for the login result.

The login failure message must be generic and stable.

Example conceptual behavior:

```text
unknown username -> AuthenticationError
wrong password   -> AuthenticationError
```

Both cases should expose equivalent external information.

Do not catch unexpected exceptions only to hide them.

If `pwdlib` cannot recognize or verify a malformed or unsupported stored password hash, treat authentication as failed.

`AuthService.login()` must convert this condition to the same generic `AuthenticationError` used for invalid credentials.

Do not expose the stored hash or password-library exception details in the public error message.

---

# Transaction Policy

Authentication foundation methods in this feature are read-only.

Therefore:

- Do not call `session.commit()`.
- Do not call `session.rollback()`.
- Do not create a Session solely for `AuthService`.
- Do not mutate User entities.

If a later approved logout design requires a database write, that behavior must be specified separately before implementation.

---

# Tests

## Test Strategy

Use unit tests.

Do not require:

- a real SQLite database
- FastAPI `TestClient`
- HTTP cookies
- tokens
- API routes

Mock `UserRepository` in AuthService tests.

Use the actual User model and Role enum where practical.

Security utility tests may exercise the configured password library directly through `hash_password()` and `verify_password()`.

---

## Security Utility Tests

When the password hashing mechanism is defined and implemented, cover at minimum:

- `hash_password()` does not return the plain password
- a generated hash verifies with the correct password
- verification fails with an incorrect password
- hashing the same password is handled according to the selected library's normal secure behavior
- malformed stored hashes follow the explicitly approved error behavior

Do not assert an exact hash string unless the configured algorithm is intentionally deterministic, which password hashing normally should not be.

Do not weaken hashing configuration to make tests deterministic.

---

## AuthService Login Tests

Cover at minimum:

- Successful login
- Successful login with an email-address-form username
- `UserRepository.find_by_username()` receives the supplied username unchanged
- Correct password returns `CurrentUserResponse`
- Role is serialized as the expected API-facing string
- Unknown username raises `AuthenticationError`
- Wrong password raises `AuthenticationError`
- Unknown username and wrong password use the same public error message
- Password hash is not included in the response
- Login does not mutate the User
- Login does not perform transaction commits

Do not test token or cookie creation.

---

## Current User Tests

If `get_current_user()` can be implemented unambiguously, cover:

- Existing User returns `CurrentUserResponse`
- `UserRepository.find_by_id()` receives the supplied user ID
- Role is serialized correctly
- Missing User raises the approved exception
- No transaction commit occurs

---

## Logout Tests

Do not add logout tests in this feature.

`AuthService.logout()` is intentionally outside the scope of this Authentication Foundation feature.

---

# Required Verification

Run from `backend/`.

Run the focused authentication tests using the actual paths created by this feature, for example:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/core/test_security.py tests/services/test_auth_service.py
```

If only one of those test modules is valid because the feature is intentionally stopped or scoped differently, report exactly what was executed.

Then run:

```bash
git diff --check
```

Then attempt:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

If the full suite encounters the known timeout in `test_application_error_uses_common_response`:

- Report the timeout accurately.
- Confirm whether the authentication-focused tests passed independently.
- Do not modify the unrelated exception-handler test in this feature.
- Do not claim the full suite passed.

Run an existing linter or formatter only when already configured in the project.

Do not add a dependency only for formatting.

---

# Completion Report

When implementation is complete, report:

## Summary

- Security utilities implemented
- AuthService methods implemented
- Tests added

## Modified Files

List every modified and new file.

## Security Behavior

Report:

- password hashing library
- password hashing algorithm/configuration
- source that established that choice
- implemented security utility functions

Do not print actual password hashes or passwords.

## AuthService Methods

List each implemented public method.

Explicitly state whether `logout()` was implemented and why.

## Authentication Behavior

Summarize:

- User lookup
- Password verification
- Login failure behavior
- Current User retrieval
- Role conversion
- Whether authentication state is created or modified

## Transaction Behavior

Confirm:

- Authentication foundation methods are read-only
- No commits occur
- No database session was introduced unnecessarily

## Tests

Report each executed command and exact result.

## Design Compliance

Confirm:

- No API routes added
- No authentication dependency added
- No cookie/session/token mechanism invented
- No authorization rules added
- No User model or migration changes
- No unrelated refactoring

## Issues or Ambiguities

List unresolved issues. If none remain, state that none remain.

## Remaining Work

State which items remain, such as:

- API authentication integration
- logout transport/state handling if not yet defined
- authorization dependencies
- AI
- Attachment/Storage
- remaining API Layer work

---

# Stop Conditions

Stop and report before continuing if any of the following is found:

- The available `pwdlib[argon2]` version cannot support `PasswordHash.recommended()` as required by the detailed design.
- Existing stored password hashes cannot be verified by the established `pwdlib` / Argon2 mechanism and require a migration or compatibility policy.
- `AuthenticationError` construction or required error code is ambiguous.
- Implementing authentication requires a User model or database migration change.
- Implementing authentication requires changing the existing authentication DTO contract.
- A required Repository method is missing or incompatible.
- Existing code already implements authentication differently from the latest design.
- Authentication implementation would require adding an HTTP-specific concern to the Service Layer.
- An unrelated test failure would require changing code outside this feature.

Do not resolve authentication or security decisions by guessing.
