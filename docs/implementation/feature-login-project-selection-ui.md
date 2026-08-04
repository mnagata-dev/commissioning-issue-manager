# Frontend Foundation + Login & Project Selection UI Implementation Guide

## Purpose

Implement the first Frontend increment for the Commissioning Issue Manager (CIM).

This task establishes the approved HTML + JavaScript Frontend foundation and implements the authenticated workflow from Login to Project Selection.

The implementation must connect the new browser UI to the existing JSON REST APIs without redesigning the Backend, authentication, domain model, API contracts, or error format.

Store this file as:

```text
docs/implementation/feature-login-project-selection-ui.md
```

---

# Implementation Scope

Implement the following:

- repository-root `frontend/` directory
- Login page
- Project Selection page
- shared CSS
- shared JavaScript API module
- shared authentication and selected-Project helpers
- Login page behavior
- Project Selection page behavior
- Cookie-based Session integration
- selected Project storage in `sessionStorage`
- logout behavior
- FastAPI delivery of approved Frontend files
- Frontend route and static-file tests
- focused regression tests
- full Backend test-suite verification
- manual UI verification where practical

The approved workflow is:

```text
Login
  │
  ▼
Project Selection
  │
  ▼
Issue List
```

This task implements Login and Project Selection only.

The Issue List UI is not implemented in this task. Project selection must still navigate to the approved future URL:

```text
/issues.html
```

Do not create an undocumented temporary Issue List, placeholder application, dashboard, or alternate destination.

---

# Source of Truth

Before editing, read the latest project documents in the priority defined by `AGENTS.md`.

Read at minimum:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
- `docs/project_conventions.md`
- `docs/requirements/requirements.md`
- `docs/design/basic_design.md`
- `docs/design/api_design.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/adr/ADR-001-user-in-control.md`

Inspect the current implementation before creating files or changing code:

- `backend/app/main.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/projects.py`
- `backend/app/api/deps.py`
- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/project.py`
- `backend/tests/api/test_auth.py`
- `backend/tests/api/test_projects.py`
- `backend/tests/test_main.py`
- existing application factory and route-registration tests
- existing repository-root directory structure
- existing `.gitignore`
- existing Frontend files, if any

Follow the actual repository structure if a listed path differs.

Do not create duplicate routes, helpers, tests, settings, or Frontend files.

---

# Branch and Git Rules

Work only on:

```text
feature/login-project-selection-ui
```

Before implementation, verify:

```bash
git branch --show-current
git status --short
```

Expected branch:

```text
feature/login-project-selection-ui
```

The following user-authored changes already belong to this task and must be preserved:

- `README.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/implementation/feature-login-project-selection-ui.md`

Do not discard, overwrite, revert, normalize, or silently rewrite those changes.

Do not:

- commit
- push
- create a Pull Request
- merge
- switch branches
- rewrite Git history
- force push
- amend an existing commit
- stage unrelated files

If the current branch differs from the assigned branch, stop before editing.

If unrelated user changes are present, preserve them and report them.

---

# Documentation Policy

The approved design documents have already been updated for this task.

Do not modify:

- Requirements
- Basic Design
- API Design
- UI Design
- Detailed Design
- Test Design
- ADRs
- Project Conventions
- AGENTS.md
- CONTRIBUTING.md

unless the user explicitly approves another documentation change.

The implementation guide itself is an existing user-authored task file. Preserve its contents.

If implementation reveals a conflict or missing specification:

1. stop;
2. report the exact documents and sections involved;
3. describe the minimum decision required;
4. do not resolve the conflict by assumption;
5. do not modify design documents automatically.

Implementation must not become the source of truth.

---

# Approved Technology and Constraints

Use:

- HTML
- CSS
- JavaScript
- browser-native ES modules
- browser-native `fetch()`
- browser-native `sessionStorage`
- FastAPI
- Starlette `StaticFiles`
- Starlette or FastAPI `FileResponse`
- existing Cookie-based Session authentication
- existing Backend JSON APIs

Do not introduce:

- React
- TypeScript
- JSX
- npm
- Node.js tooling
- package.json
- bundlers
- transpilers
- Vite
- Webpack
- Parcel
- Babel
- CSS frameworks
- JavaScript frameworks
- templating engines
- another Frontend server
- a reverse proxy
- CORS changes
- authentication tokens
- localStorage-based authentication
- new runtime dependencies

No build step is allowed.

The Frontend must be directly served by the existing FastAPI application.

---

# Approved Frontend Structure

Create or complete the following structure at the repository root:

```text
frontend/
├── index.html
├── projects.html
├── css/
│   └── style.css
└── js/
    ├── api.js
    ├── auth.js
    ├── login.js
    └── projects.js
```

Do not create additional Frontend source files unless the existing repository already has an approved equivalent or a genuinely necessary test file requires it.

In particular, do not add:

- `issues.html`
- component frameworks
- template fragments
- copied vendor files
- generated assets
- minified files
- source maps
- lock files
- Node metadata

The Frontend is intentionally small.

---

# Approved Browser URLs

Implement the following delivery routes:

|URL|Delivered file|
|---|---|
|`/`|`frontend/index.html`|
|`/projects.html`|`frontend/projects.html`|
|`/css/*`|files under `frontend/css/`|
|`/js/*`|files under `frontend/js/`|

The following remains an approved navigation destination but is out of scope to serve in this task:

```text
/issues.html
```

The existing REST API remains under:

```text
/api/*
```

Do not change any existing API path.

Frontend page routes must not be included in the OpenAPI schema.

Static file mounts must not interfere with `/api/*`.

---

# Frontend Delivery Architecture

Use the existing FastAPI application factory.

The application must:

- return `frontend/index.html` for `GET /`
- return `frontend/projects.html` for `GET /projects.html`
- mount `frontend/css/` at `/css`
- mount `frontend/js/` at `/js`
- preserve all existing API routers
- preserve all existing exception handlers
- preserve Session middleware behavior
- preserve the existing application factory contract
- preserve existing test configuration behavior
- keep Frontend routes out of OpenAPI

Resolve the repository-root Frontend directory safely from application source location.

Do not rely on the process current working directory.

The application must work when started from the expected Backend directory and when imported by tests.

Use a stable path based on `Path(__file__).resolve()` or an existing approved project-root helper.

Do not:

- use hard-coded machine-specific absolute paths
- use `/home/nagata/...`
- use Windows-specific paths
- change the working directory
- search the filesystem dynamically
- fall back to an unrelated directory
- silently create missing Frontend files at runtime

Missing required Frontend files are implementation or deployment errors. Do not generate them dynamically.

---

# Route Registration Rules

Register Frontend page routes and static mounts in a way that does not shadow existing API routes.

Required API behavior must remain unchanged.

When ordering routes or mounts, verify that:

- `/api/auth/login` still resolves to the Login API
- `/api/auth/logout` still resolves to the Logout API
- `/api/auth/me` still resolves to Current User API
- `/api/projects` still resolves to Project API
- all existing Issue, Comment, Attachment, and AI routes remain reachable
- `/css/style.css` resolves as a static asset
- `/js/api.js` resolves as a static asset
- unknown API routes are not treated as Frontend pages
- unknown page routes are not silently rewritten to `/`

Do not implement SPA fallback behavior.

Do not mount the entire Frontend directory at `/`.

Use explicit HTML routes and limited static mounts as approved by Detailed Design.

---

# Existing API Contracts

Reuse the existing API contracts exactly.

Do not modify request or response schemas.

## Login API

```http
POST /api/auth/login
Content-Type: application/json
```

Request:

```json
{
  "username": "engineer1@example.com",
  "password": "password"
}
```

Success response:

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

Expected errors:

- `400 Bad Request`
- `401 Unauthorized`

## Logout API

```http
POST /api/auth/logout
```

Success response:

```json
{
  "message": "Logged out"
}
```

Expected error:

- `401 Unauthorized`

## Current User API

```http
GET /api/auth/me
```

Success response:

```json
{
  "id": 1,
  "username": "engineer1@example.com",
  "display_name": "Engineer 1",
  "role": "ENGINEER"
}
```

Expected error:

- `401 Unauthorized`

## Project List API

```http
GET /api/projects
```

Success response:

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

Expected error:

- `401 Unauthorized`

Do not add a Frontend-specific Backend API.

---

# Same-Origin Session Rules

The Frontend and Backend are delivered from the same Origin.

Use the existing Cookie-based Session.

Do not store authentication state, password, Session ID, cookie value, or user token in:

- `localStorage`
- `sessionStorage`
- URL parameters
- HTML attributes
- JavaScript constants
- cookies created by Frontend code

Browser `fetch()` must use same-origin behavior.

It is acceptable to specify:

```javascript
credentials: "same-origin"
```

consistently in the shared API helper.

Do not use:

```javascript
credentials: "include"
```

unless the existing project conventions or actual same-origin implementation already require it. Do not add cross-origin assumptions.

Do not manually read or write the Session cookie.

---

# Shared API Module

Implement shared API behavior in:

```text
frontend/js/api.js
```

The module must provide a small, explicit API request helper.

Responsibilities:

- call `fetch()`
- use same-origin credentials
- set JSON headers only when sending JSON
- parse successful JSON responses
- parse the approved common JSON error response when present
- identify HTTP status
- distinguish `401 Unauthorized`
- expose enough structured error information for page modules
- avoid leaking internal response details to the UI
- handle responses without a body safely
- avoid parsing non-JSON static responses
- avoid duplicate API request logic across page modules

The helper must not:

- manipulate page-specific DOM
- decide page-specific success navigation
- store authentication data
- store selected Project
- call `alert()`
- reload the page automatically
- invent API response fields
- swallow unexpected errors
- convert every failure into `401`
- add CSRF tokens not defined by design
- retry requests automatically
- log passwords or response bodies containing sensitive data

Use a project-local custom JavaScript error class only if it keeps handling simple and explicit.

If a custom error is used, prefer fields such as:

```text
status
code
message
```

Do not expose raw stack traces or backend internals to users.

---

# Shared Authentication and Project-State Module

Implement shared browser-state behavior in:

```text
frontend/js/auth.js
```

This module may contain small helpers for:

- obtaining the current authenticated user
- redirecting to Login
- redirecting to Project Selection
- clearing selected Project information
- reading selected Project information
- storing selected Project information
- logout
- handling common `401 Unauthorized` behavior

Keep page-specific rendering in page modules.

## Selected Project Storage

Store the selected Project identification information in `sessionStorage`.

Use one clear, project-specific storage key.

The stored value must be sufficient for later screens to identify and display the selected Project without storing authentication data.

The selected Project object may contain only fields already returned by the Project API, such as:

```json
{
  "id": 1,
  "name": "Hotel A Commissioning",
  "hotel": {
    "id": 1,
    "name": "Hotel A"
  }
}
```

Do not invent fields.

Use JSON serialization.

Reading storage must safely handle:

- missing value
- invalid JSON
- wrong primitive type
- missing Project ID
- corrupted object

When storage is invalid:

- remove the invalid value
- treat the Project as not selected
- do not crash the page

Clear selected Project information on:

- successful logout
- authenticated API `401 Unauthorized`
- invalid stored Project data

Do not use `localStorage` for selected Project.

Do not clear unrelated `sessionStorage` entries.

Avoid `sessionStorage.clear()` unless the design explicitly requires clearing all application and non-application session state. Prefer removal of the CIM key only.

---

# Login Page

Implement:

```text
frontend/index.html
frontend/js/login.js
```

## Page Purpose

Authenticate the user.

Successful authentication navigates to:

```text
/projects.html
```

## Required UI

Provide:

- CIM Login heading
- Username label
- Username input
- Password label
- Password input
- Login button
- error-message area
- loading or disabled state during API communication

Use semantic HTML.

The form must be a real HTML `<form>` so Enter submits naturally.

Required input behavior:

- username uses an appropriate text or email-capable input without preventing non-email usernames
- password uses `type="password"`
- both fields are required
- labels are explicitly associated with inputs
- button uses `type="submit"`
- browser autofill attributes are reasonable
- initial keyboard focus should be usable
- error output should be accessible to assistive technologies

Do not require JavaScript click handlers for Enter-key behavior when form submission already provides it.

## Login Page Initialization

When the Login page opens:

1. call `GET /api/auth/me`;
2. if it succeeds, navigate to `/projects.html`;
3. if it returns `401`, remain on Login;
4. if it fails for another reason, show a safe system error and allow login attempts where practical.

A `401` from the initial Current User check is an expected unauthenticated state, not a visible login failure.

Do not show “username or password is incorrect” for the initial `/api/auth/me` `401`.

Do not create a Session during the authentication check.

## Login Submission

On submit:

1. prevent duplicate submission;
2. clear the previous visible error;
3. trim or normalize only if approved by existing Backend behavior;
4. do not modify the password;
5. perform minimal required-field validation;
6. send the exact Login API JSON request;
7. on success, navigate to `/projects.html`;
8. on authentication failure, show the approved safe message;
9. on validation or system failure, show a safe user-facing message;
10. restore the interactive state after a non-navigation failure.

Do not store the returned User as authentication proof.

The response User may be ignored after a successful login because the Project page obtains the current User from `/api/auth/me`.

Do not log username/password pairs.

## Login Error Message

For authentication failure, use the approved user-facing message from UI Design:

```text
ログイン ID またはパスワードが正しくありません。
```

For unexpected failure, use the approved general style:

```text
予期しないエラーが発生しました。
時間をおいて再度お試しください。
```

Do not display:

- traceback
- exception class
- SQL
- file path
- backend error internals
- raw HTML response
- response headers
- cookie content

---

# Project Selection Page

Implement:

```text
frontend/projects.html
frontend/js/projects.js
```

## Page Purpose

Display available Projects and allow the authenticated user to select the active Project.

## Required UI

Provide:

- Project Selection heading
- current User display
- Project list
- Hotel name for each Project
- Project name for each Project
- one selectable control per Project
- Select Project button
- Logout button
- error-message area
- loading state
- empty-state message when no Projects are returned

Follow the simple, mobile-first layout in UI Design.

Use semantic and accessible controls.

A radio-group-style selection is appropriate.

Do not implement Project creation, editing, deletion, filtering, sorting controls, or Administration.

## Page Initialization Order

When Project Selection opens:

1. verify the current authenticated User using `GET /api/auth/me`;
2. if `401`, clear selected Project and navigate to `/`;
3. if authenticated, display the current User;
4. request `GET /api/projects`;
5. if Project API returns `401`, clear selected Project and navigate to `/`;
6. render the Project list;
7. restore the selected Project control only when the stored Project still appears in the current API response;
8. otherwise leave no Project selected or remove stale stored selection.

Do not trust `sessionStorage` as authorization or Project existence proof.

The API response is authoritative for the current Project list.

## Project Rendering

For each Project, display at minimum:

- `project.hotel.name`
- `project.name`

Associate the selectable control with a clear visible label.

Use DOM APIs that avoid interpreting API values as HTML.

Do not insert Project or Hotel names through unsafe `innerHTML`.

Prefer:

- `document.createElement()`
- `textContent`
- explicit attribute assignment

If a small fixed template is used, never interpolate untrusted API strings into HTML.

## Project Selection

The Select Project button must not proceed without a selected Project.

If no Project is selected, show a clear user-facing validation message.

On valid selection:

1. find the complete Project object in the latest API result;
2. store its approved identification information in `sessionStorage`;
3. navigate to:

```text
/issues.html
```

Do not fetch Issue data in this task.

Do not create or serve `issues.html` in this task.

Do not silently choose the first Project.

Do not persist selection in `localStorage`.

## Empty Project List

When the API returns:

```json
{
  "projects": []
}
```

show a clear empty state.

Do not treat an empty Project list as an API error.

Disable or make the Select Project action ineffective until a Project exists and is selected.

Do not create demo Projects.

---

# Logout Behavior

Project Selection must provide Logout.

On Logout:

1. prevent duplicate submission;
2. call `POST /api/auth/logout`;
3. on success, remove the selected Project storage key;
4. navigate to `/`;
5. do not preserve authentication state in browser storage.

If Logout returns `401`:

- treat the Session as no longer usable;
- remove selected Project information;
- navigate to `/`.

If Logout fails with another status or network error:

- do not falsely claim success;
- show a safe user-facing error;
- preserve current page state unless the response proves authentication is invalid.

Do not call `sessionStorage.clear()` unless required by the actual approved implementation. Remove only the CIM selected-Project key.

---

# Common 401 Handling

For authenticated API calls, `401 Unauthorized` means:

- the Session is missing, expired, invalid, or references a missing User;
- selected Project state must be cleared;
- the browser must navigate to `/`.

This applies at minimum to:

- `GET /api/auth/me` on Project Selection
- `GET /api/projects`
- `POST /api/auth/logout`

On the Login page, `GET /api/auth/me` returning `401` is expected and must not cause a redirect loop.

Do not implement global behavior that redirects a failed Login request back to the page already being displayed.

The API helper may identify a `401`, but page/auth logic must apply context-appropriate behavior.

---

# CSS Requirements

Implement shared styling in:

```text
frontend/css/style.css
```

Follow:

- Mobile First
- Simple UI
- clear readable typography
- usable touch targets
- clear labels
- visible focus states
- sufficient spacing
- readable error messages
- clear disabled/loading state
- PC-browser usability

Keep styles modest.

Do not create a design system or large utility framework.

Do not import:

- Google Fonts
- CDN CSS
- third-party icons
- third-party reset libraries
- JavaScript widgets

The UI must work without internet access.

Prefer system fonts.

Provide styles for at minimum:

- page body
- centered or constrained main content
- headings
- forms
- labels
- text/password inputs
- buttons
- disabled buttons
- error or alert area
- loading text
- Project list
- Project selection item
- current User area
- empty state
- Logout action

Do not hide focus outlines without an accessible replacement.

Do not rely on color alone to communicate errors or selection.

---

# HTML Security and Quality Rules

Each page must include:

- `<!doctype html>`
- language declaration
- UTF-8 charset
- viewport metadata
- meaningful `<title>`
- semantic main content
- correct CSS link
- JavaScript loaded as ES modules

Use absolute same-origin asset paths approved by design:

```text
/css/style.css
/js/login.js
/js/projects.js
```

Do not use inline event handlers such as:

```html
onclick="..."
```

Do not embed credentials, environment values, API responses, or configuration secrets in HTML.

Do not use `document.write()`.

Do not render API data with unsafe HTML injection.

Do not add Content Security Policy or security headers in this task unless already required by existing architecture.

---

# JavaScript Module Rules

Use browser-native ES modules.

Keep responsibilities separated:

|Module|Responsibility|
|---|---|
|`api.js`|HTTP and API error handling|
|`auth.js`|authentication helpers, navigation, selected Project storage, logout|
|`login.js`|Login page DOM and workflow|
|`projects.js`|Project Selection page DOM and workflow|

Avoid circular imports.

Avoid global variables on `window`.

Avoid a single large script containing all functionality.

Do not create generic abstractions beyond the current two pages.

Do not prematurely build:

- component framework
- router
- global state store
- event bus
- dependency-injection container
- model layer
- validation framework
- localization framework

Prefer small named functions.

Use `const` by default and `let` only when reassignment is required.

Use clear identifiers and explicit control flow.

---

# Loading and Duplicate-Action Rules

During Login, Project loading, Project confirmation, and Logout:

- prevent duplicate action where applicable;
- disable the relevant button or form controls;
- provide a visible processing state;
- restore controls after a failure that does not navigate away.

Do not leave controls disabled after handled errors.

Do not start the same initialization request multiple times.

Avoid race conditions between:

- authentication check
- Project list loading
- logout
- selection confirmation

Do not over-engineer cancellation unless actual implementation needs it.

---

# Error Handling Rules

The Backend common error format is:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed."
  }
}
```

Frontend may use the approved safe Backend message when appropriate, but must not rely on every failure containing valid JSON.

Handle:

- approved JSON error response
- empty response body
- malformed JSON
- network failure
- unexpected content type
- unexpected HTTP status

For unexpected errors, show a generic safe message.

Do not expose internal details.

Do not put raw error objects into `textContent` if they may contain implementation details.

Console logging must not expose:

- passwords
- cookies
- Session identifiers
- full sensitive request bodies

Avoid unnecessary console output in committed code.

---

# Backend Change Limits

Backend changes should be limited to Frontend delivery and related tests.

Expected Backend changes may include:

- `backend/app/main.py`
- `backend/tests/test_main.py`
- one focused Frontend-delivery test file if that better matches existing test organization

Do not modify:

- API contracts
- Pydantic schemas
- Service methods
- Repository methods
- database models
- migrations
- database constraints
- authentication rules
- Session contents
- password handling
- error-response format
- AI integration
- Attachment storage
- configuration unless a true design-approved requirement exists

No new runtime dependency is expected.

If a new runtime or development dependency appears necessary, stop before modifying `pyproject.toml` or `uv.lock`.

---

# Static File Security Rules

Static delivery must expose only the approved CSS and JavaScript directories.

Do not expose:

- repository root
- Backend source
- `.env`
- database files
- storage files
- Git files
- documentation directory
- arbitrary absolute paths

Rely on `StaticFiles` path handling for mounted directories.

Do not implement custom arbitrary file-path endpoints.

HTML routes must return only the two approved HTML files.

Do not accept a user-controlled path parameter for page files.

---

# OpenAPI Policy

Frontend routes are not API contract routes.

Set the explicit page routes to:

```python
include_in_schema=False
```

Verify that OpenAPI still contains only the approved REST API paths.

Do not add:

- `/`
- `/projects.html`
- `/css/...`
- `/js/...`

to OpenAPI.

Do not weaken the existing approved-route test merely to make it pass.

Update tests only to account for intentionally added non-OpenAPI routes or mounts.

---

# Testing Policy

Follow `docs/design/test_design.md`.

UI details are primarily manual in the initial release, but deterministic delivery and JavaScript structure should be tested where practical without introducing a JavaScript test toolchain.

Do not add Node.js solely for tests.

Use existing Python/FastAPI testing for:

- HTML delivery
- static file delivery
- content type
- OpenAPI exclusion
- API regression
- route conflicts

Use manual browser verification for:

- form submission
- Enter-key behavior
- visible error display
- redirect behavior
- Project selection
- `sessionStorage`
- Logout
- mobile-width usability

If the environment does not permit browser testing, report it accurately.

Do not claim manual browser verification was completed unless it was actually performed.

---

# Required Automated Tests

Add or update tests to verify the following.

## Login Page Delivery

Verify:

- `GET /` returns `200`
- response content type is HTML
- response contains the Login page rather than JSON
- required Login form elements are present
- page references `/css/style.css`
- page references `/js/login.js`
- page route is absent from OpenAPI

Avoid brittle full-document string equality.

Use stable markers such as IDs, labels, titles, or script paths.

## Project Selection Page Delivery

Verify:

- `GET /projects.html` returns `200`
- response content type is HTML
- response contains the Project Selection page
- required Project container exists
- Logout control exists
- page references `/css/style.css`
- page references `/js/projects.js`
- page route is absent from OpenAPI

## Static CSS Delivery

Verify:

- `GET /css/style.css` returns `200`
- response content type is CSS
- response is non-empty

## Static JavaScript Delivery

Verify at minimum:

- `GET /js/api.js` returns `200`
- `GET /js/auth.js` returns `200`
- `GET /js/login.js` returns `200`
- `GET /js/projects.js` returns `200`
- response content type is JavaScript-compatible
- each response is non-empty

Do not require one exact content-type spelling if Starlette uses a standards-compliant equivalent with charset.

## Route and OpenAPI Regression

Verify:

- all previously approved API routes remain present
- no duplicate API methods are introduced
- `/` is not in OpenAPI
- `/projects.html` is not in OpenAPI
- static mounts are not in OpenAPI
- `/api/projects` still resolves as JSON API
- `/api/auth/me` still resolves as JSON API

## Missing and Unknown Resources

Where stable with existing framework behavior, verify:

- unknown CSS file returns `404`
- unknown JavaScript file returns `404`
- unknown API route remains an API `404`
- no SPA fallback serves Login HTML for unknown paths

Do not add fragile tests for framework-internal route representations unless needed.

---

# JavaScript Verification Without Node

Because npm and build tools are out of scope, do not introduce a JavaScript unit-test framework.

Perform practical static verification where supported:

- inspect module import paths
- confirm all referenced files exist
- confirm no syntax errors through an available browser or JavaScript runtime only if already installed
- do not add a dependency merely to run syntax checks

Python tests may verify key static source properties when that remains maintainable, but avoid tests that duplicate the entire implementation text.

Do not assert every internal function name.

Focus on observable contract and safety-critical properties.

---

# Manual UI Verification

When practical, run the FastAPI application in the approved local development environment and verify in a browser.

## Login

Verify:

- `/` displays Login
- username and password are usable
- Enter submits the form
- required-field behavior is understandable
- invalid credentials show the approved message
- successful Login navigates to `/projects.html`
- opening `/` while authenticated navigates to `/projects.html`
- no authentication data appears in `sessionStorage`

## Project Selection

Verify:

- current User is displayed
- Project list loads
- Hotel and Project names are displayed
- no Project is silently selected
- selecting a Project and confirming stores approved Project information
- selection navigates to `/issues.html`
- browser `sessionStorage` contains selected Project only
- invalid or stale stored JSON does not break the page
- empty Project list is displayed safely
- expired Session returns to `/`

The `/issues.html` navigation may result in `404` because Issue List delivery is explicitly outside this task. Report that accurately; do not implement an unapproved placeholder.

## Logout

Verify:

- Logout calls the existing API
- selected Project information is removed
- browser navigates to `/`
- the previous Session can no longer access authenticated API behavior

## Layout

Verify at least:

- narrow mobile viewport remains usable
- controls are not clipped
- form labels remain visible
- buttons are touch-friendly
- error text is readable
- desktop width remains reasonable

---

# Test Fixtures and Isolation

Use the existing test application factory and dependency override patterns.

Do not require a production database merely to test static files.

For tests that call authenticated APIs, reuse existing fixtures or override dependencies as the project already does.

Do not duplicate full authentication integration fixtures when existing tests already cover them.

Frontend route tests should not mutate global application state in a way that leaks between tests.

Preserve current settings-injection behavior.

---

# Required Verification Commands

Run from the repository root or Backend directory as appropriate.

Before tests:

```bash
git branch --show-current
git status --short
git diff --check
```

Focused Frontend delivery and application tests should include the actual created test paths.

Example:

```bash
cd backend
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/test_main.py \
  tests/test_frontend.py
```

If no separate `test_frontend.py` is created, run the relevant actual test files.

Run existing authentication and Project API regression tests:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/api/test_auth.py \
  tests/api/test_projects.py \
  tests/test_main.py
```

Run the full Backend suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q
```

Run Python compile verification:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
```

Run final whitespace verification from repository root:

```bash
git diff --check
```

Inspect final status and diff:

```bash
git status --short
git diff --stat
git diff -- \
  backend/app/main.py \
  backend/tests \
  frontend \
  README.md \
  docs/design/ui_design.md \
  docs/design/detailed_design.md \
  docs/design/test_design.md \
  docs/implementation/feature-login-project-selection-ui.md
```

Do not assume example file names exist. Use actual modified files in final commands.

If `~/.cache/uv` is not writable, use:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache
```

Do not modify project dependency files merely to work around cache permissions.

---

# Existing TestClient Constraint

Previous tasks observed environment-specific TestClient or AnyIO blocking in some sandbox runs.

If the same issue occurs:

1. confirm whether it reproduces in an existing API test;
2. do not misreport it as a Frontend-specific implementation failure;
3. use the already approved executable environment if available;
4. record the exact command and result;
5. do not claim tests passed if they were only collected.

Do not skip the full suite silently.

---

# Self-Review Requirements

Before completion, review the entire diff.

Confirm all of the following.

## Scope

- only Login, Project Selection, Frontend foundation, delivery, and tests were implemented
- Issue List UI was not implemented
- no placeholder application was added
- no unrelated refactor was included
- no Backend API contract changed
- no DB or migration changed
- no dependency changed

## Frontend Architecture

- `frontend/` is at repository root
- only approved files were added
- HTML + CSS + JavaScript are used
- no build step exists
- ES modules load through approved paths
- same-origin API calls are used
- responsibilities are separated across modules

## Authentication

- Cookie-based Session is reused
- Login request matches API contract
- Current User is checked on page initialization
- Login-page `401` is treated as expected unauthenticated state
- authenticated users are redirected away from Login
- Project-page `401` clears selected Project and redirects to Login
- credentials are not stored in browser storage
- cookie values are not manually accessed

## Selected Project

- selected Project uses `sessionStorage`
- only API-returned identification information is stored
- invalid stored JSON is handled safely
- stale selection is not trusted
- Logout clears the selected Project key
- `401` clears the selected Project key
- unrelated session storage is preserved

## UI

- Login form is semantic
- Enter submission works naturally
- labels are associated with controls
- Project list is accessible
- Hotel and Project names use safe text rendering
- no unsafe API-data HTML injection exists
- loading and error states are visible
- no external internet asset is required
- mobile-first usability is maintained

## Delivery

- `/` returns Login HTML
- `/projects.html` returns Project Selection HTML
- `/css` exposes only CSS directory
- `/js` exposes only JavaScript directory
- application paths are independent of current working directory
- API routes remain reachable
- unknown routes do not receive SPA fallback
- Frontend routes are absent from OpenAPI

## Tests

- focused tests pass
- auth/project regressions pass
- full suite passes
- compile verification passes
- `git diff --check` passes
- manual tests are reported honestly
- warnings are described accurately

---

# Explicitly Out of Scope

Do not implement:

- Issue List page
- Issue Detail page
- Issue Create page
- Issue Edit page
- Comment UI
- Attachment UI
- AI Draft UI
- Administration UI
- Project administration
- User administration
- Master Data administration
- Room APIs
- Frontend routing framework
- SPA behavior
- offline support
- service workers
- PWA manifest
- WebSocket
- notifications
- dark mode
- internationalization
- custom accessibility framework
- automated browser test framework
- React migration
- TypeScript migration
- Node.js setup
- deployment redesign
- Docker
- reverse proxy
- CORS changes
- CSRF redesign
- new authentication mechanism
- API schema changes
- Backend business-logic changes
- database changes
- dependency updates

Do not add future work merely because it would make this task feel complete.

---

# Stop Conditions

Stop immediately and report before continuing if any of the following occurs.

## Branch or Working Tree

- current branch is not `feature/login-project-selection-ui`
- user-authored design changes would be overwritten
- unrelated changes cannot be safely preserved
- implementation guide is missing or conflicts with the task

## Design Conflict

- approved URL and actual intended URL differ
- Login or Project response differs from API Design
- UI Design and Detailed Design conflict
- selected Project storage rules conflict
- Logout behavior is ambiguous
- Issue List destination requires an unapproved placeholder
- documents disagree on HTML/JavaScript versus React/TypeScript

## Architecture Conflict

- static delivery requires another server
- same-origin delivery cannot be implemented with current application factory
- `/css` or `/js` mounts would shadow existing API routes
- repository-root Frontend cannot be resolved safely
- existing application startup assumes files unavailable in tests
- implementation requires CORS, reverse proxy, or SPA fallback

## Existing-Code Conflict

- existing Frontend files implement a different approved architecture
- equivalent shared modules already exist under different names
- `main.py` has a route policy incompatible with design
- existing route tests require removal or weakening of approved API guarantees
- existing Session behavior differs from API Design

## Dependency or Tooling Expansion

- a new Python dependency is needed
- npm or Node tooling appears necessary
- a JavaScript test framework is required
- `pyproject.toml` or `uv.lock` would need modification
- external CDN assets appear necessary

## Scope Expansion

- Issue List must be implemented for the flow to proceed
- a new Backend API seems necessary
- Project data must be changed
- authentication state must be stored in browser storage
- design changes are needed
- unrelated cleanup or refactoring becomes necessary

When stopping, preserve all existing work and provide:

- exact conflict
- affected files
- commands already run
- tests already run
- minimum decision needed
- modified files
- remaining work

---

# Completion Report

At the end, report exactly these sections.

## Summary

Describe:

- Frontend foundation implemented
- Login behavior implemented
- Project Selection behavior implemented
- static delivery implemented
- tests added
- whether manual browser verification was performed

Do not claim Issue List UI is implemented.

## Modified Files

List every modified and added file.

Separate:

- implementation changes
- tests
- existing user-authored documentation preserved

## Tests

List every command run and its result.

Include:

- focused tests
- authentication/Project regression
- full suite
- compile verification
- `git diff --check`
- manual verification or why it was not performed
- warnings
- environment constraints
- interrupted or failed attempts

Do not omit failed intermediate runs.

## Design Compliance

Confirm at minimum:

- HTML + JavaScript only
- no npm/build tool
- same-origin FastAPI delivery
- existing JSON APIs reused
- Cookie-based Session reused
- no auth data in storage
- selected Project in `sessionStorage`
- `401` handling
- Logout cleanup
- safe DOM rendering
- OpenAPI unchanged
- no API/DB/dependency change
- Issue List out of scope

## Assumptions

Use:

```text
None.
```

unless a genuine assumption was required and permitted.

Do not hide assumptions.

## Remaining Work

State remaining implementation work accurately.

Expected out-of-scope next step:

```text
Issue List UI remains for a later task.
```

If selection navigates to an unserved `/issues.html`, state that this is expected because Issue List delivery is outside this task.

Do not report “None” if the approved workflow still reaches an out-of-scope page.

---

# Completion Criteria

This task is complete only when all applicable criteria are satisfied.

- correct branch used
- user-authored changes preserved
- approved Frontend directory created
- Login page implemented
- Project Selection page implemented
- shared CSS implemented
- shared API module implemented
- shared auth/storage helpers implemented
- FastAPI page delivery implemented
- CSS and JavaScript static mounts implemented
- existing API routes preserved
- Frontend routes excluded from OpenAPI
- Login authentication check implemented
- Login submission implemented
- authenticated Login redirect implemented
- Project authentication check implemented
- Project list rendering implemented
- selected Project validation implemented
- selected Project stored in `sessionStorage`
- invalid stored Project handled safely
- authenticated API `401` clears Project and redirects
- Logout clears Project and redirects
- no authentication data stored
- no unsafe API-data HTML injection
- no React or TypeScript introduced
- no npm or build tools introduced
- no new dependencies introduced
- no Issue List UI introduced
- focused tests pass
- existing auth and Project tests pass
- full Backend suite passes
- compile verification passes
- `git diff --check` passes
- full diff self-reviewed
- completion report is accurate
- no commit, push, PR, or merge performed

Do not mark the task complete if required automated verification fails.

Do not mark the task complete if the implementation differs from approved design.

Do not mark the task complete if unapproved files, dependencies, APIs, or UI features were added.
