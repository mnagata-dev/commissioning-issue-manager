# API Authentication Integration Implementation Guide

## Feature

`feature/api-auth`

---

## Purpose

Implement the API Authentication Integration for the Commissioning Issue Manager (CIM).

This feature connects the existing Authentication Foundation to FastAPI HTTP requests using the approved Cookie-based Session design.

It is responsible for:

- Session configuration
- Starlette `SessionMiddleware`
- Authentication dependencies
- Authentication API routes
- Login Session creation
- Current User resolution from Session
- Logout Session deletion
- focused authentication / authorization dependency tests

This file is the Codex implementation instruction for this feature and must be stored as:

```text
docs/implementation/feature-api-auth.md
```

The implementation must follow the latest repository design documents and current code.

Do not invent another authentication mechanism, token format, Session store, cookie policy, authorization model, or public API contract.

---

# Read First

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

In particular, confirm that the latest repository versions define the approved authentication mechanism as:

- Cookie-based Session
- Starlette `SessionMiddleware`
- Session data contains only `user_id`
- cookie name `cim_session`
- `HttpOnly=True`
- `SameSite=lax`
- `Secure=False` for the initial local HTTP environment
- cookie path `/`
- Session max age 8 hours
- Session secret from `CIM_SESSION_SECRET`
- no default Session secret
- application must not start without the Session secret
- no JWT / Bearer Token / Refresh Token
- no Server-side Session Database

Inspect the current implementation before editing, especially:

- `backend/app/main.py`
- `backend/app/api/deps.py`
- `backend/app/api/routes/`
- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/db/session.py`
- `backend/app/models/user.py`
- `backend/app/models/enums.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/__init__.py`
- `backend/app/services/auth_service.py`
- `backend/app/core/security.py`
- existing API tests
- existing authentication tests
- `backend/tests/conftest.py`
- `backend/pyproject.toml`
- `backend/uv.lock`

Do not assume an attached copy of a document is newer than the repository version.

If the latest design documents and repository code do not provide enough information to implement this feature without guessing, apply the Stop Conditions below.

Do not modify design documents unless the user has already made and staged an approved design clarification before implementation begins.

---

# Current Design Contract

The current approved design establishes the following.

## Authentication Credentials

Users authenticate with:

- `username`
- `password`

`username` is the login ID and may use an email-address format.

Password hashing and verification are already owned by the Authentication Foundation.

Do not redesign password hashing in this feature.

---

## Existing AuthService Contract

The existing Authentication Foundation provides:

```python
login(username: str, password: str) -> CurrentUserResponse

get_current_user(user_id: int) -> CurrentUserResponse
```

`AuthService` does not own HTTP Session state.

Do not add:

```python
AuthService.logout(...)
```

Logout is an API Layer responsibility because the approved initial authentication state exists only in the HTTP Session Cookie.

---

## Authentication State

Authentication state uses Cookie-based Session.

The HTTP Session implementation is Starlette `SessionMiddleware`.

The Session must contain only the authenticated User ID:

```python
{
    "user_id": 1
}
```

Do not store any of the following in Session:

- username
- display name
- role
- password
- password hash
- Project selection
- access-control decisions
- arbitrary User model data

When current User information is required, resolve the Session `user_id` through:

```python
AuthService.get_current_user(user_id)
```

---

## Session Cookie Contract

Use the approved Session Cookie settings:

|Setting|Value|
|---|---|
|Cookie name|`cim_session`|
|Session data|`user_id` only|
|HttpOnly|`True`|
|SameSite|`lax`|
|Secure|`False`|
|Path|`/`|
|Max Age|8 hours|

Eight hours is:

```text
28800 seconds
```

Do not change these values in this feature.

Do not add a second authentication cookie.

Do not make the cookie readable by frontend JavaScript.

Do not set `Secure=True` in the initial local HTTP configuration merely as a generic security improvement; the current design explicitly defines `Secure=False` for this environment.

---

## Session Secret Contract

The Session signing secret is owned by `app/core/config.py`.

Use:

```text
CIM_SESSION_SECRET
```

There is no default value.

The application must not start when the Session secret is missing or empty.

The secret must never be hard-coded in source code, tests committed as a real deployment secret, logs, exception messages, or API responses.

Tests may use an explicit test-only value through environment configuration.

Do not add the secret to the database.

---

## Authentication API Contract

Implement exactly these endpoints:

```text
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

Use the request and response DTOs already defined in the repository whenever they match the approved API Design.

Do not change public request or response shape merely for implementation convenience.

---

## Error Contract

Use the existing project custom exceptions and common exception handler.

Expected mappings include:

```text
AuthenticationError -> 401 Unauthorized
AuthorizationError  -> 403 Forbidden
```

Do not raise FastAPI `HTTPException` from AuthService.

The API Layer should rely on the existing application exception mechanism unless the existing implementation clearly establishes another approved convention.

Do not expose Session contents, Session secret, password data, password hashes, or internal exception details in public error responses.

---

# Scope

Implement only the approved API Authentication Integration.

Expected implementation areas are:

- Session secret configuration
- application startup validation for the required Session secret
- `SessionMiddleware` registration
- Authentication Dependency
- AuthService dependency construction
- Role authorization dependency defined by the current Detailed Design
- Authentication API router
- authentication route registration
- focused API / dependency / configuration tests
- minimal dependency update only when required for Starlette Session support

Keep changes small and focused.

---

# Out of Scope

Do not implement in this feature:

- JWT
- Bearer-token authentication
- Access Tokens
- Refresh Tokens
- token revocation
- OAuth
- OpenID Connect
- Server-side Session Database
- Redis Session storage
- database-backed Session tables
- user-login history tables
- user creation API
- password change API
- password reset flow
- account lockout
- rate limiting
- MFA
- Remember Me behavior
- sliding Session expiration unless already provided by the approved middleware behavior
- frontend Login implementation
- frontend route guards
- Project selection persistence
- business API routes unrelated to Authentication
- Attachment API integration
- AI API integration unless already present and only authentication wiring is explicitly required
- Issue API implementation
- Comment API implementation
- Administration API implementation
- database schema changes
- Alembic migrations
- User model changes
- UserRepository redesign
- AuthService redesign
- password hashing changes
- public Schema redesign
- unrelated CORS redesign
- dedicated CSRF token implementation
- unrelated refactoring

Do not add a generic authentication framework.

Do not add a second Session mechanism.

---

# Expected Directory Structure

Follow the current repository structure rather than creating a parallel API framework.

Expected additions or modifications may include:

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── core/
│   │   └── config.py
│   └── main.py
└── tests/
    ├── api/
    │   └── test_auth.py
    ├── test_config.py
    └── ...
```

Use the existing API-test directory convention if the repository already uses another location.

Do not create empty placeholder files.

Do not rename existing modules without an approved need.

---

# Dependencies and Configuration

## Session Secret

Add the Session secret to the existing `Settings` model using the existing configuration convention.

Conceptually:

```python
session_secret: str | None = None
```

Read:

```text
CIM_SESSION_SECRET
```

No default secret is allowed.

Treat both missing and empty configuration as invalid for application startup.

The exact internal exception type for invalid application configuration is not a public API contract. Follow the existing configuration/application-factory convention and keep the implementation minimal.

Do not create a broad configuration validation framework solely for this feature.

---

## Starlette Session Support

Use Starlette `SessionMiddleware` as required by the Detailed Design.

Do not install a separate authentication/session framework.

If the currently installed Starlette version requires an additional small runtime dependency such as `itsdangerous` for `SessionMiddleware`, first verify whether it is already available through the current dependency graph.

If it is genuinely required and absent, adding that direct runtime dependency is permitted.

Do not upgrade FastAPI, Starlette, or unrelated dependencies merely to implement Session support.

Record any dependency change in `pyproject.toml` and `uv.lock` through the normal `uv` workflow.

---

# Application Startup and SessionMiddleware

Register `SessionMiddleware` in the existing application factory / application creation flow.

Use the configured Session secret.

Configure the middleware according to the approved contract:

```text
secret key     = CIM_SESSION_SECRET
session cookie = cim_session
max age        = 28800
same site      = lax
https only     = False
path           = /
```

Use the actual parameter names supported by the installed Starlette version.

Do not hard-code the Session secret.

Do not add middleware in module-global side effects if the existing project uses an application factory.

Preserve the existing application-factory design.

Application creation/startup must fail when `CIM_SESSION_SECRET` is not configured.

Do not silently generate a random secret at startup because that would invalidate Sessions on restart and violate the approved required-configuration contract.

Do not use a development default such as:

```text
secret
changeme
dev-secret
```

---

# Authentication Dependency Construction

Reuse existing database Session and Repository boundaries.

A Dependency may construct the authentication Service from the current request-scoped database Session.

Conceptual dependency chain:

```text
DB Session
   ↓
UserRepository
   ↓
AuthService
   ↓
Authentication Dependency
```

A helper such as the following is acceptable when consistent with existing project style:

```python
get_auth_service(...) -> AuthService
```

Do not query SQLAlchemy directly in the authentication dependency.

Do not duplicate User lookup logic in the API Layer.

The API Layer may construct Repository and Service objects through dependency injection; business/data-access behavior remains in their existing layers.

---

# `get_current_user` Dependency

Implement the Authentication Dependency defined by the Detailed Design.

Conceptual behavior:

```python
get_current_user(...) -> CurrentUserResponse
```

Processing:

1. Read the request Session.
2. Read `user_id` from Session.
3. If `user_id` is absent, raise `AuthenticationError`.
4. Call:

```python
auth_service.get_current_user(user_id)
```

5. Return the resulting `CurrentUserResponse`.

If `AuthService.get_current_user()` reports that the User no longer exists, preserve the existing `AuthenticationError` behavior so the API returns `401 Unauthorized`.

Do not:

- verify Passwords here
- query User directly here
- perform role authorization here
- create Session state here
- clear Session state here
- commit or rollback transactions here
- convert authentication failure to `NotFoundError`

Do not silently accept missing authentication.

Do not redirect to a Login page from the API Dependency.

---

# Session Payload Validation Boundary

The approved Session payload consists of `user_id` only.

At minimum, detect absence of `user_id` as unauthenticated.

Do not invent broader Session payload schemas, Session versioning, device IDs, roles, usernames, or Project context.

If the existing middleware can produce an empty Session when the cookie is missing or invalid, treat that as unauthenticated through the normal missing-`user_id` behavior.

Do not expose whether a cookie signature was invalid.

---

# `require_administrator` Dependency

The Detailed Design defines a separate authorization dependency:

```python
require_administrator(
    user: CurrentUserResponse,
) -> CurrentUserResponse
```

Implement this dependency only as the approved Role boundary.

Behavior:

- receive an already-authenticated `CurrentUserResponse`
- allow `ADMINISTRATOR`
- reject non-Administrator users with `AuthorizationError`
- return the same authenticated user on success

Do not:

- re-read the Session
- re-query the database
- verify the Password
- implement Project-level authorization
- implement Issue-level authorization
- create Administration APIs

No current Engineer-facing API should be restricted merely because this dependency exists.

Apply it only to endpoints that the latest API design explicitly defines as Administrator-only.

If no such API route exists in the current feature, keep the dependency reusable but do not invent a route solely to exercise it.

---

# Authentication API Router

Implement the authentication router according to the approved API Design.

Preserve the current project router-registration convention.

Do not change unrelated routes.

---

# `POST /api/auth/login`

## Request

Use the existing Login request DTO matching:

```json
{
  "username": "engineer1@example.com",
  "password": "password"
}
```

Do not normalize, lowercase, trim, or rewrite `username` unless the existing Schema or AuthService already defines that behavior.

---

## Processing

The approved flow is:

1. Read Username and Password from the Login Request.
2. Call:

```python
auth_service.login(username, password)
```

3. On successful authentication, save only:

```python
request.session["user_id"] = current_user.id
```

4. Return the approved Login Response.

Do not call `AuthService.get_current_user()` again after successful login unless existing code requires it for a defined reason.

Do not store the whole `CurrentUserResponse` in Session.

Do not store credentials in Session.

Do not create a token.

---

## Login Response

Preserve the API Design response shape:

```json
{
  "user": {
    "id": 1,
    "username": "engineer1@example.com",
    "display_name": "Engineer 1",
    "role": "ENGINEER"
  }
}
```

Reuse an existing `LoginResponse` schema if present and correct.

If the repository currently has no dedicated response DTO but the exact API response can be produced without changing the public contract, use the existing project response convention rather than inventing a broader Schema redesign.

Do not return `password_hash`.

---

## Login Failure

Unknown Username and wrong Password are already handled by `AuthService.login()` as the same public authentication failure.

Do not reveal which credential component was wrong.

On authentication failure:

- do not create a new authenticated Session
- return the existing `AuthenticationError` response through the common exception handler
- expected HTTP status is `401 Unauthorized`

Do not clear an already-existing authenticated Session on a failed Login attempt unless the latest design explicitly requires that behavior.

The current approved contract only requires that failed authentication does not create a Session.

---

# `GET /api/auth/me`

Use the Authentication Dependency.

Approved flow:

1. Authentication Dependency reads Session `user_id`.
2. Dependency calls `AuthService.get_current_user(user_id)`.
3. Route returns `CurrentUserResponse`.

Preserve the API Design response shape:

```json
{
  "id": 1,
  "username": "engineer1@example.com",
  "display_name": "Engineer 1",
  "role": "ENGINEER"
}
```

Do not query the User again in the route.

Do not return Session data directly.

When authentication state is missing or invalid, return `401 Unauthorized` through the common exception contract.

---

# `POST /api/auth/logout`

Logout is an API Layer responsibility.

Require the request to be authenticated before clearing Session state.

Approved flow:

1. Resolve the current User using the Authentication Dependency.
2. Clear the request Session:

```python
request.session.clear()
```

3. Return:

```json
{
  "message": "Logged out"
}
```

Do not add `AuthService.logout()`.

Do not perform a database write.

Do not create a token blacklist or revocation table.

After successful Logout, the previous Session must no longer authenticate requests.

Unauthenticated Logout returns `401 Unauthorized`.

---

# Cookie Behavior

Session cookie behavior must be provided by the approved `SessionMiddleware` configuration.

Tests should verify externally observable cookie policy without depending on Starlette's private serialization format.

Verify at minimum that successful Login results in a Session cookie with the approved properties:

- cookie name `cim_session`
- `HttpOnly`
- `SameSite=lax`
- `Path=/`
- `Max-Age=28800`
- no `Secure` attribute in the initial HTTP configuration

Do not decode or assert the exact signed-cookie bytes unless necessary for a focused test.

Do not assert Starlette private implementation details.

Logout should cause the authenticated Session state to be removed/invalidated according to the middleware behavior.

---

# CSRF Boundary

The approved initial design states:

- Frontend and Backend are same-origin.
- Session cookie uses `SameSite=lax`.
- a dedicated CSRF Token is not introduced in the initial version.
- state-changing operations use appropriate non-GET HTTP methods.
- GET requests must not modify business data.
- CORS must not allow arbitrary origins.

Therefore, in this feature:

- do not add a CSRF-token framework
- do not add a CSRF cookie
- do not add hidden CSRF fields
- do not change HTTP methods to work around CSRF
- do not add permissive `Access-Control-Allow-Origin: *` behavior

If the existing application already has a CORS configuration that permits arbitrary origins and that conflicts with the approved design, stop and report the conflict rather than silently redesigning CORS in this feature.

---

# Authorization Boundary

Authentication answers:

```text
Who is the current User?
```

Authorization answers:

```text
May this User perform this operation?
```

Keep these concerns separate.

`get_current_user` performs authentication only.

`require_administrator` performs the approved Role check only.

Do not add role checks to `AuthService.login()` or `AuthService.get_current_user()`.

Do not add role values to Session.

Do not infer new Role policies beyond the approved design.

---

# Database and Transaction Policy

This feature must not add or change database persistence.

Authentication API integration is read-only with respect to business/database state.

Therefore:

- no database schema changes
- no Alembic migration
- no Session table
- no token table
- no login history table
- no User mutation
- no `commit()` for login/me/logout
- no `rollback()` solely for authentication state

The SQLAlchemy request Session may be used through the existing Repository / AuthService dependency chain for User lookup.

Do not perform direct SQLAlchemy queries in API routes or authentication dependencies.

---

# Error Handling

Preserve existing project error handling.

## Authentication Failures

Expected `401 Unauthorized` cases include:

- unknown Username
- wrong Password
- no Session cookie / no Session state
- Session without `user_id`
- Session `user_id` whose User no longer exists
- use of the previous Session after Logout
- unauthenticated Logout

The public Login failure must not reveal Username existence.

---

## Authorization Failures

`require_administrator()` must use `AuthorizationError` for a non-Administrator authenticated User.

Expected HTTP status:

```text
403 Forbidden
```

Do not convert authorization failure to `401` merely because Authentication and Authorization are implemented in the same module.

---

## Internal Errors

Do not expose:

- Session secret
- signed Session value
- Password
- Password Hash
- stack traces
- internal dependency wiring

Unexpected errors should continue through the existing common error mechanism.

Do not catch broad exceptions solely to make tests pass.

---

# Tests

Use FastAPI `TestClient` for HTTP integration tests as defined by Test Design.

Reuse existing test fixtures and dependency overrides where practical.

Do not rewrite the whole test infrastructure.

Do not make tests depend on a real deployment Session secret.

Set a dedicated test secret explicitly in test environment/configuration.

---

## Configuration Tests

Cover at minimum:

- `CIM_SESSION_SECRET` can be read from environment
- no hard-coded default Session secret exists
- application creation/startup fails when the Session secret is missing
- application creation/startup fails when the Session secret is empty, when the current Settings convention treats empty as missing
- test application can start with an explicit test Session secret

Do not assert or print the real secret value.

---

## SessionMiddleware / Cookie Tests

Cover externally observable behavior:

- successful Login creates `cim_session`
- cookie is `HttpOnly`
- cookie uses `SameSite=lax`
- cookie path is `/`
- cookie Max-Age is 28800 seconds
- cookie is not marked `Secure` in the initial local HTTP design
- authenticated follow-up requests use the Session successfully

Do not assert private Starlette signer internals.

---

## Login API Tests

Cover at minimum:

- successful Login
- email-address-format Username can log in
- successful Login returns the approved response shape
- successful Login creates authenticated Session state
- unknown Username returns `401`
- wrong Password returns `401`
- unknown Username and wrong Password expose equivalent public authentication information
- failed Login does not create a new authenticated Session
- response never includes `password_hash`

Use existing Authentication Foundation tests as authoritative for low-level password hashing behavior; do not duplicate every password utility test at API level.

---

## Current User API Tests

Cover at minimum:

- authenticated request returns current User
- no Session returns `401`
- Session without `user_id` returns `401`
- Session with a `user_id` whose User does not exist returns `401`
- response matches the approved `CurrentUserResponse` shape

Use dependency-level tests where constructing a specific Session state is clearer and less coupled than forging Starlette's signed cookie format.

Do not weaken Session signing merely to create test data.

---

## Logout API Tests

Cover at minimum:

- authenticated Logout succeeds
- Logout returns:

```json
{
  "message": "Logged out"
}
```

- unauthenticated Logout returns `401`
- after Logout, the same client can no longer call an authenticated API successfully
- after Logout, `/api/auth/me` returns `401`
- Logout performs no database mutation

Do not add an AuthService logout mock because no AuthService logout method exists.

---

## Authentication Dependency Tests

Cover at minimum:

- Session `user_id` is passed to `AuthService.get_current_user()`
- returned `CurrentUserResponse` is propagated
- missing `user_id` raises `AuthenticationError`
- invalid/nonexistent authenticated User follows `AuthenticationError`
- no direct Repository query is introduced inside the dependency

Avoid assertions against incidental dependency-construction details that would make harmless refactoring difficult.

---

## Administrator Dependency Tests

If `require_administrator()` is implemented in this feature, cover:

- Administrator is accepted
- the same `CurrentUserResponse` is returned
- Engineer raises `AuthorizationError`
- no database query occurs
- authentication and authorization remain separate

Do not create an Administration API merely for this test.

---

# Existing Tests

Do not weaken, delete, skip, or rewrite existing tests merely to make this feature pass.

Authentication Foundation tests remain authoritative for:

- password hashing
- password verification
- AuthService credential behavior
- generic Login authentication failure
- AuthService current-user behavior

Repository tests remain authoritative for User lookup persistence behavior.

Common error-handler tests remain authoritative for project-wide error response format.

If an unrelated existing test fails, report it rather than modifying unrelated code.

---

# Required Verification

Run from `backend/`.

First run focused tests using the actual paths created or modified by this feature, for example:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/api/test_auth.py tests/test_config.py
```

Also run existing Authentication Foundation regression tests:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest tests/core/test_security.py tests/services/test_auth_service.py
```

If dependency tests are stored separately, include them in the focused run.

Then run:

```bash
git diff --check
```

Then attempt the full suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest
```

The repository has previously exhibited a known timeout around:

```text
tests/test_main.py::test_application_error_uses_common_response
```

If that unrelated timeout remains:

- report it accurately
- report how many tests were collected if known
- confirm the focused API Authentication tests independently passed
- do not modify the unrelated exception-handler test in this feature
- do not claim the full suite passed

When useful, also run the suite excluding only that known test:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -k 'not test_application_error_uses_common_response'
```

Run an existing formatter/linter only if already configured.

Do not add a new tool only for this feature.

---

# Design Compliance

Before completion, confirm all of the following:

- Cookie-based Session is used
- Starlette `SessionMiddleware` is used
- Session contains only `user_id`
- cookie name is `cim_session`
- `HttpOnly=True`
- `SameSite=lax`
- `Secure=False`
- Path is `/`
- Max Age is 8 hours / 28800 seconds
- Session secret comes from `CIM_SESSION_SECRET`
- no default secret exists
- application refuses to start without the secret
- Login uses existing `AuthService.login()`
- Current User uses existing `AuthService.get_current_user()`
- Logout clears Session in API Layer
- no `AuthService.logout()` is added
- unauthenticated requests return `401`
- authorization failure returns `403`
- no credentials or Password Hash are stored in Session
- no JWT / Bearer / Refresh Token is added
- no Server-side Session Database is added
- no database schema/migration changes are made
- no direct SQLAlchemy queries are added to API/dependencies
- no unrelated business API implementation is included
- no frontend implementation is included
- no unrelated refactoring is included

---

# Git Rules

Work only on the feature branch prepared by the user.

Expected branch:

```text
feature/api-auth
```

Before editing, verify the current branch.

Do not create or switch branches unless requested.

Do not:

- commit
- push
- merge
- amend
- reset
- rebase
- force push
- discard user changes
- overwrite staged design changes

Preserve the user's latest design-document changes.

---

# Completion Report

When implementation is complete, report using the following structure.

## Summary

Summarize the API Authentication Integration implemented.

Include:

- Session configuration
- middleware
- authentication dependencies
- authentication routes
- tests

## Modified Files

List every modified and new file.

Distinguish any design-document changes that existed before Codex implementation and were preserved unchanged.

## Session Configuration

Report:

- environment variable name
- cookie name
- max age
- HttpOnly
- SameSite
- Secure
- Path
- startup behavior when secret is missing

Do not report the secret value.

## Authentication Dependencies

Report implemented dependencies and behavior.

Include:

- current User resolution
- missing Session behavior
- invalid User behavior
- Administrator dependency if implemented

## Authentication API

Report implementation status for:

```text
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

## Login Behavior

Summarize:

- AuthService call
- Session `user_id` creation
- response shape
- failure behavior

## Logout Behavior

Confirm:

- authenticated requirement
- Session clear behavior
- no AuthService logout method
- no database write
- previous Session no longer authenticates

## Cookie Behavior

Report the externally verified cookie attributes.

Do not print signed cookie contents.

## Error Behavior

Summarize:

- AuthenticationError -> 401
- AuthorizationError -> 403
- generic credential failure behavior
- no sensitive information exposure

## Tests

Report every command and exact result.

Do not report the full suite as passed if it timed out or skipped a test.

## Design Compliance

Confirm:

- no JWT/token mechanism
- no Server-side Session Database
- no database/migration changes
- no AuthService redesign
- no public API contract changes
- no dedicated CSRF token implementation
- no unrelated routes
- no frontend changes
- no unrelated refactoring

## Issues or Ambiguities

List unresolved issues.

If none remain, state that none remain.

## Remaining Work

List only work outside this feature, such as:

- authentication wiring into remaining protected business API routes if those routes are not yet implemented
- remaining API Layer implementation
- Attachment API integration
- AI API integration if still pending
- Frontend Login / authenticated navigation
- real-environment browser verification
- HTTPS cookie-policy update when deployment moves to HTTPS
- known unrelated exception-handler timeout investigation

---

# Stop Conditions

Stop and report before continuing if any of the following is found:

- The latest approved design no longer specifies Cookie-based Session.
- The latest approved design conflicts with `SessionMiddleware` usage.
- Cookie name, Max Age, SameSite, Secure, or Path differs between current design documents.
- `CIM_SESSION_SECRET` ownership or required/no-default behavior is contradictory.
- The existing Settings/application-factory design cannot enforce required Session configuration without a broader configuration redesign.
- The installed Starlette version cannot support the approved Session cookie contract.
- Required SessionMiddleware runtime support would require an unapproved major framework/dependency change.
- Existing authentication state is already implemented with JWT, Bearer Token, Server-side Session, or another mechanism that conflicts with the latest design.
- Existing Login / Logout / Current User API contracts differ from the latest approved API Design.
- Implementing the approved API would require changing public authentication DTOs.
- Existing `AuthService.login()` or `AuthService.get_current_user()` behavior conflicts with the latest approved design.
- `AuthenticationError` does not map to `401` as required.
- `AuthorizationError` does not map to `403` as required when `require_administrator()` is implemented.
- Logout cannot be implemented as API-layer Session clearing with the installed middleware behavior.
- Implementing Session authentication requires a database model or migration change.
- Implementing authentication would require direct SQLAlchemy queries in API routes/dependencies.
- Existing CORS configuration permits arbitrary origins in a way that conflicts with the approved CSRF policy.
- Existing application startup tests require a behavior that conflicts with mandatory `CIM_SESSION_SECRET` configuration.
- A required authentication request/response Schema is missing or contradictory and implementing it would require choosing a new public contract.
- An unrelated test failure would require changing code outside this feature.
- Latest Requirements, API Design, Detailed Design, and Test Design conflict on required authentication behavior.

Do not resolve Session, cookie, secret, authentication, authorization, CSRF, public API, or dependency decisions by guessing.

---

# Acceptance Criteria

This feature is complete only when all applicable criteria below are satisfied:

- `CIM_SESSION_SECRET` configuration implemented
- application refuses to start without required Session secret
- `SessionMiddleware` configured according to approved design
- Authentication Dependency implemented
- `POST /api/auth/login` implemented
- `GET /api/auth/me` implemented
- `POST /api/auth/logout` implemented
- successful Login creates authenticated Session state
- Current User resolves through Session `user_id`
- Logout clears Session state
- previous Session cannot authenticate after Logout
- unauthenticated access returns `401`
- Administrator dependency implemented if unambiguously required by current Detailed Design
- non-Administrator authorization failure returns `403`
- focused authentication API tests pass
- existing Authentication Foundation tests pass
- `git diff --check` passes
- full regression status is reported accurately
- no database/migration change
- no public API redesign
- no token authentication
- no unrelated implementation

---

# Notes

This feature closes the boundary intentionally left open by `feature/auth`.

The Authentication Foundation owns credential verification and User resolution.

This feature owns HTTP authentication state and authentication API integration.

The responsibility boundary is:

```text
Browser
   │
   │ cim_session Cookie
   ▼
SessionMiddleware
   │
   │ request.session["user_id"]
   ▼
Authentication Dependency
   │
   ▼
AuthService.get_current_user()
   │
   ▼
CurrentUserResponse
```

Login creates the approved Session state in the API Layer.

Logout removes the approved Session state in the API Layer.

AuthService remains independent of HTTP Cookie and Session concerns.
