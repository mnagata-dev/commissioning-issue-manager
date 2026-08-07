# Issue List UI Implementation Guide

## Purpose

Implement the Issue List UI for the Commissioning Issue Manager (CIM).

This task extends the existing HTML + CSS + JavaScript Frontend foundation and connects the Issue List screen to the existing authenticated Issue List API.

Store this file as:

```text
docs/implementation/feature-issue-list-ui.md
```

---

# Implementation Scope

Implement:

- `frontend/issues.html`
- `frontend/js/issues.js`
- minimal additions to `frontend/css/style.css`
- FastAPI delivery of `/issues.html`
- current User and selected Project display
- selected Project validation
- initial unfiltered Issue List
- Keyword, Status, Category, and Target Type filters
- `All` options for optional select filters
- fixed `page_size=20`
- Previous and Next page controls
- current page and total count display
- loading, empty, and error states
- `401 Unauthorized` handling
- missing/invalid selected Project handling
- Project `404` handling
- Change Project and Logout
- Frontend delivery and regression tests
- full Backend verification
- manual browser verification where practical

The implemented flow is:

```text
Login
  │
  ▼
Project Selection
  │
  ▼
Issue List
```

---

# Explicit Scope Boundary

Do not implement:

- Issue Detail UI
- Issue Create UI
- Issue Edit UI
- Comment UI
- Attachment UI
- AI Draft UI

The approved URLs are:

- Issue Detail: `/issue.html?issue_id={issue_id}`
- Issue Create: `/issue-create.html`

Implement navigation from Issue List to these approved URLs.

Do not implement the destination pages, placeholder pages, or temporary routes in this task.

---

# Source of Truth

Before editing, read the latest:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
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

Inspect:

- `backend/app/main.py`
- `backend/tests/test_frontend.py`
- `backend/tests/test_main.py`
- `frontend/index.html`
- `frontend/projects.html`
- `frontend/css/style.css`
- `frontend/js/api.js`
- `frontend/js/auth.js`
- `frontend/js/login.js`
- `frontend/js/projects.js`
- existing Issue API routes and tests

Follow the actual repository structure if paths differ.

Do not create duplicate helpers, routes, storage keys, or static mounts.

---

# Branch and Git Rules

Work only on:

```text
feature/issue-list-ui
```

Before implementation:

```bash
git branch --show-current
git status --short
```

Expected branch:

```text
feature/issue-list-ui
```

Preserve existing user-authored changes, including when present:

- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/implementation/feature-issue-list-ui.md`

Do not:

- commit
- push
- create a Pull Request
- merge
- switch branches
- rewrite Git history
- force push
- amend
- stage unrelated files

If the branch differs, stop before editing.

---

# Documentation Policy

The design documents have already been updated.

Do not modify Requirements, Design documents, ADRs, Project Conventions, AGENTS.md, or CONTRIBUTING.md unless explicitly approved.

If implementation reveals a conflict:

1. stop;
2. report the exact documents and sections;
3. describe the minimum decision required;
4. do not guess;
5. do not modify documentation automatically.

---

# Approved Technology and Constraints

Use:

- HTML
- CSS
- JavaScript
- browser-native ES modules
- browser-native `fetch()`
- browser-native `sessionStorage`
- existing shared Frontend modules
- existing FastAPI application
- existing Cookie-based Session authentication
- existing JSON REST APIs

Do not introduce:

- React
- TypeScript
- JSX
- npm
- Node.js tooling
- package.json
- bundlers
- transpilers
- CSS or JavaScript frameworks
- another Frontend server
- reverse proxy
- CORS changes
- authentication tokens
- new runtime dependencies

No build step is allowed.

---

# Approved Frontend Structure

```text
frontend/
├── index.html
├── projects.html
├── issues.html
├── css/
│   └── style.css
└── js/
    ├── api.js
    ├── auth.js
    ├── login.js
    ├── projects.js
    └── issues.js
```

Do not add Issue Detail/Create/Edit files or Node metadata.

---

# Browser URL

Implement:

|URL|Delivered file|
|---|---|
|`/issues.html`|`frontend/issues.html`|

Existing routes must remain unchanged.

The page route must not appear in OpenAPI.

Do not implement SPA fallback.

---

# Existing Issue List API

Use exactly:

```http
GET /api/projects/{project_id}/issues
```

Query parameters:

|Parameter|Required|Default|Validation|
|---|---|---|---|
|`status`|No|-|approved Status|
|`category`|No|-|approved Category|
|`target_type`|No|-|`ROOM` or `OTHER`|
|`keyword`|No|-|-|
|`page`|No|`1`|1 or greater|
|`page_size`|No|`20`|1 to 100|

Response:

```json
{
  "items": [
    {
      "id": 101,
      "room": {
        "id": 1,
        "room_number": "1203"
      },
      "target_type": "ROOM",
      "target": null,
      "category": "LIGHTING",
      "description": "Bathroom light does not turn off.",
      "status": "OPEN",
      "updated_at": "2026-06-30T10:30:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

Errors:

- `400`: invalid query
- `401`: unauthenticated
- `404`: Project not found

Do not change the API contract.

---

# Approved Values

## Status

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

## Category

```text
LIGHTING
SHADE
KEYPAD
SENSOR
TSTAT
PROCESSOR
NETWORK
SERVER
INTEGRATION
OTHER
```

## Target Type

```text
ROOM
OTHER
```

Do not use superseded ADR values such as ROOM_TYPE, AREA, HOTEL, or GENERAL.

---

# Selected Project State

Reuse the selected Project state already implemented in `frontend/js/auth.js`.

Do not create a second storage key or parser.

Expected shape:

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

Handle safely:

- missing value
- invalid JSON
- primitive value
- missing/invalid Project ID
- malformed name or Hotel data

When unusable:

1. remove only the CIM selected Project key;
2. navigate to `/projects.html`;
3. do not call the Issue API;
4. do not clear unrelated session storage.

---

# Initialization Flow

On `/issues.html`:

1. read and validate selected Project;
2. if invalid, navigate to `/projects.html`;
3. call `GET /api/auth/me`;
4. if `401`, clear selected Project and navigate to `/`;
5. display current User and Project;
6. request page 1 with no optional filters and `page_size=20`;
7. render the result.

Do not use browser storage as authentication proof.

---

# Shared Module Reuse

Reuse:

```text
frontend/js/api.js
frontend/js/auth.js
```

Do not duplicate:

- fetch wrappers
- API error parsing
- selected Project logic
- `401` handling
- Logout logic
- navigation helpers

Modify shared modules only when a small reusable addition is truly necessary.

---

# Issue List HTML

`frontend/issues.html` must include:

- semantic document structure
- shared CSS
- `issues.js` as an ES module
- current Project display
- current User display
- Logout
- Change Project
- search form
- Keyword input
- Status select
- Category select
- Target Type select
- Search button
- loading state
- error area
- Issue list container
- empty state
- total count
- current page
- Previous button
- Next button

Use stable IDs or data attributes for tests.

Do not use inline event handlers.

---

# Search Initial State

All conditions are optional.

Initial state:

- Keyword empty
- Status `All`
- Category `All`
- Target Type `All`

Initial request must include:

```text
page=1
page_size=20
```

It must omit unused filters.

Do not submit empty parameters such as:

```text
status=
category=
target_type=
keyword=
```

Do not apply example values like OPEN or LIGHTING by default.

---

# Search Execution

On Search:

1. prevent default submission;
2. reset page to `1`;
3. collect form values;
4. omit unused filters;
5. request the API;
6. render result;
7. update page, total, and pagination state.

Use `URLSearchParams` or equivalent safe encoding.

Do not implement client-side business filtering.

---

# Pagination

Use fixed:

```text
page_size=20
```

Previous is enabled only when:

```text
page > 1
```

Next is enabled only when:

```text
page * page_size < total
```

On Previous/Next:

- preserve current filters;
- request the new page;
- update list and pagination state.

Do not allow page 0 or negative pages.

Disable pagination controls while loading.

---

# Issue Rendering

For each Issue display:

- Status
- Room for `ROOM`
- Target for `OTHER`
- Category
- Description
- Updated At

Use safe DOM APIs such as:

- `document.createElement()`
- `textContent`

Do not interpolate API data into unsafe `innerHTML`.

## ROOM

Display:

```text
Room 1203
```

If Room data is missing, show a safe fallback and do not crash.

## OTHER

Display:

```text
Target: Network
```

If Target is missing, show a safe fallback and do not crash.

## Unknown Target Type

Do not treat it as ROOM or OTHER. Show a safe generic fallback.

## Description

Display plain text. CSS truncation is acceptable.

Do not add Read More because Issue Detail is out of scope.

## Updated At

Use browser-native date formatting only.

Handle invalid values safely.

---

# Empty State

An empty `items` array with `total=0` is not an error.

Show a clear message such as:

```text
該当するIssueはありません。
```

Keep search controls visible.

Disable pagination as appropriate.

Do not create demo Issues.

---

# Loading State

During requests:

- show loading feedback;
- disable Search;
- disable Previous/Next;
- prevent duplicate requests.

After completion or handled failure, restore valid control states.

Do not leave controls disabled.

---

# Error Handling

## `400`

Show a safe search error.

Do not navigate away.

## `401`

1. remove selected Project;
2. navigate to `/`;
3. stop rendering protected data.

## `404` Project Not Found

1. remove selected Project;
2. clear stale Issue display;
3. navigate to `/projects.html`.

## Unexpected Error

Show:

```text
予期しないエラーが発生しました。
時間をおいて再度お試しください。
```

Do not expose internal details.

---

# Change Project

On Change Project:

1. remove only the selected Project key;
2. navigate to `/projects.html`.

Do not log out.

---

# Logout

Reuse the existing shared Logout behavior.

On success or `401`:

1. remove selected Project;
2. navigate to `/`.

On another failure, show a safe error and preserve current page state.

---

# Issue Detail and Issue Create Controls

Use the approved URLs:

- Issue Detail: `/issue.html?issue_id={issue_id}`
- Issue Create: `/issue-create.html`

Implement the Open Issue and New Issue navigation controls.

Do not implement the destination pages, placeholder files, or temporary routes in this task.

---

# CSS Requirements

Update `frontend/css/style.css` minimally.

Add styles for:

- header actions
- current Project/User
- search form
- filter controls
- Issue list/cards
- badges
- Room/Target label
- Description excerpt
- Updated At
- pagination
- loading
- empty state
- error state
- disabled controls

Maintain Mobile First, visible focus, readable text, touch-friendly controls, and offline operation.

Do not import external assets or frameworks.

---

# Accessibility

Use semantic HTML.

Associate labels with controls.

Use text on buttons.

Expose disabled states correctly.

Do not rely on color alone for Status.

Use native HTML semantics before ARIA.

---

# Backend Change Limits

Expected Backend changes:

- add `/issues.html` delivery in `backend/app/main.py`
- update Frontend delivery tests
- update route/OpenAPI regression tests if needed

Do not modify:

- Issue API
- Service
- Repository
- schemas
- models
- migrations
- authentication
- Session configuration
- error format
- dependencies

If a new dependency appears necessary, stop before changing:

```text
backend/pyproject.toml
backend/uv.lock
```

---

# FastAPI Delivery

Serve:

```text
GET /issues.html
```

using the existing explicit HTML delivery pattern.

Set:

```python
include_in_schema=False
```

Do not depend on current working directory.

Do not mount the entire Frontend directory at `/`.

Do not add SPA fallback.

---

# Required Automated Tests

## HTML Delivery

Verify:

- `GET /issues.html` returns `200`
- content type is HTML
- Issue List page markers exist
- `/css/style.css` is referenced
- `/js/issues.js` is referenced
- search controls exist
- list and pagination containers exist
- Logout and Change Project controls exist
- `/issues.html` is absent from OpenAPI

## JavaScript Delivery

Verify:

- `GET /js/issues.js` returns `200`
- JavaScript-compatible content type
- non-empty response

## Regression

Verify:

- `/` still serves Login
- `/projects.html` still serves Project Selection
- unknown pages remain `404`
- no SPA fallback
- `/api/auth/me`, `/api/projects`, and Issue List API remain JSON
- approved API paths remain unchanged
- no duplicate routes

Avoid brittle full-document equality.

---

# Manual Browser Verification

When practical, verify:

## Initialization

- authenticated selected Project opens `/issues.html`
- current User and Project display
- filters start empty/All
- initial request uses page 1 and page size 20
- no optional filters are sent
- Issues display in API order

## Missing Project

- removing selected Project redirects to `/projects.html`
- Issue API is not called

## Authentication Failure

- expired Session redirects to `/`
- selected Project is removed

## Search

- Keyword
- Status
- Category
- Target Type
- combined filters
- All omits optional parameters
- new Search resets to page 1

## Pagination

- Previous disabled on page 1
- Next works when more results exist
- filters persist across pages
- Next disabled on last page
- total count displayed

## Rendering

- ROOM displays Room
- OTHER displays Target
- Description is plain text
- empty results show empty state

## Actions

- Change Project redirects to `/projects.html`
- Logout redirects to `/`
- no authentication data is stored
- unrelated session storage is preserved

Do not claim manual verification if not completed.

---

# Required Verification Commands

Before implementation:

```bash
git branch --show-current
git status --short
git diff --check
```

Focused tests:

```bash
cd backend
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/test_frontend.py \
  tests/test_main.py
```

Issue API regression:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/api/test_issues.py \
  tests/test_frontend.py \
  tests/test_main.py
```

Auth and Project regression:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/api/test_auth.py \
  tests/api/test_projects.py
```

Full suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q
```

Compile:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
```

Final checks from repository root:

```bash
git diff --check
git status --short
git diff --stat
```

Inspect actual changed files with `git diff -- ...`.

---

# Existing TestClient Constraint

If TestClient/AnyIO blocks in the sandbox:

1. confirm it reproduces in an existing test;
2. do not label it an Issue List failure;
3. use the already approved executable environment if available;
4. record exact commands and results;
5. do not claim tests passed when only collected.

---

# JavaScript Syntax Verification

Do not install Node.js.

If an existing JavaScript runtime is available, syntax checking may be used.

If unavailable, report it and rely on static review, browser verification where possible, and delivery tests.

---

# Self-Review Checklist

Confirm:

## Scope

- only Issue List UI, delivery, minimal shared support, and tests changed
- no Detail/Create/Edit destination UI added
- no unrelated refactor
- no API/DB/dependency change

## Frontend

- `issues.html` and `issues.js` exist
- shared API/auth modules reused
- one selected Project key
- no duplicate fetch wrapper
- same-origin requests
- no build step

## Authentication and Selection

- invalid Project redirects to `/projects.html`
- `401` clears Project and redirects to `/`
- Project `404` clears Project and redirects to `/projects.html`
- no auth data stored
- unrelated session storage preserved

## Search

- initial no-filter request
- exact approved values
- Search resets page 1
- unused filters omitted
- safe URL encoding
- no client-side business filtering

## Pagination

- page size 20
- Previous/Next boundary logic correct
- filters preserved
- page 0 impossible
- duplicate requests prevented

## Rendering

- ROOM/OTHER display correct
- plain-text safe rendering
- malformed data does not crash
- empty state works
- Status visible as text

## Delivery and Tests

- `/issues.html` works
- OpenAPI unchanged
- API routes reachable
- no SPA fallback
- focused and full tests pass
- compile and `git diff --check` pass
- manual verification reported honestly

---

# Stop Conditions

Stop immediately if:

- branch is not `feature/issue-list-ui`
- user changes would be overwritten
- design documents disagree on values or page size
- Issue Detail/Create navigation is required without approved URLs
- existing shared modules require redesign
- `/issues.html` cannot be added safely
- a new dependency or Node tooling is needed
- API/schema/Service/Repository/DB changes are needed
- Room API is needed
- design documents need further updates
- unrelated cleanup becomes necessary

Report:

- exact conflict
- affected files
- commands/tests already run
- minimum decision needed
- modified files
- remaining work

---

# Completion Report

Use exactly:

## Summary

## Modified Files

Separate implementation, tests, and preserved user documentation.

## Tests

Include all commands, results, warnings, failed attempts, JavaScript verification, and manual browser status.

## Design Compliance

Confirm:

- HTML + CSS + JavaScript only
- no npm/build tool
- existing JSON API and Cookie Session reused
- selected Project reused from `sessionStorage`
- invalid Project, `401`, and Project `404` handling
- initial no-filter request
- All options
- page size 20
- Previous/Next
- safe DOM rendering
- OpenAPI unchanged
- no API/DB/dependency changes
- no undocumented URLs
- Detail/Create remain out of scope

## Assumptions

```text
None.
```

unless a genuine permitted assumption was required.

## Remaining Work

Expected:

```text
Issue Detail UI and Issue Create UI remain for later tasks.
```

---

# Completion Criteria

Complete only when:

- correct branch used
- user changes preserved
- `frontend/issues.html` added
- `frontend/js/issues.js` added
- shared CSS updated minimally
- `/issues.html` delivery added and excluded from OpenAPI
- current User/Project displayed
- selected Project validated
- initial unfiltered Issue List loaded
- all four filters implemented
- All options implemented
- Search resets page 1
- unused filters omitted
- page size fixed at 20
- Previous/Next and boundaries implemented
- page and total displayed
- ROOM/OTHER rendering implemented
- loading, empty, and error states implemented
- `401` and Project `404` behavior implemented
- Change Project and Logout implemented
- no unsafe API-data HTML injection
- no React/TypeScript/npm/build tools
- no new dependencies
- no undocumented URLs
- no Detail/Create UI
- focused, regression, and full tests pass
- compile and `git diff --check` pass
- full diff reviewed
- no commit, push, PR, or merge performed

Do not mark complete if required verification fails or unapproved changes were added.
