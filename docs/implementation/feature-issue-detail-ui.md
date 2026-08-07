# Issue Detail UI Implementation Guide

## Purpose

Implement the Issue Detail UI for the Commissioning Issue Manager (CIM).

This task extends the existing HTML + CSS + JavaScript Frontend and connects the Issue Detail screen to the existing authenticated Issue, Comment, and Attachment APIs.

Store this file as:

```text
docs/implementation/feature-issue-detail-ui.md
```

---

# Implementation Scope

Implement:

- `frontend/issue.html`
- `frontend/js/issue.js`
- minimal additions to `frontend/css/style.css`
- FastAPI delivery of `/issue.html`
- Issue ID parsing from `?issue_id={issue_id}`
- Issue Detail loading
- ROOM / OTHER detail rendering
- Status, Category, Description, creator/updater, and timestamps where supported by the existing response
- Comment list rendering
- Attachment list rendering
- navigation to the approved Issue Edit URL
- Add Comment within the Issue Detail page
- Upload Attachment within the Issue Detail page
- Open Attachment behavior
- Back navigation to Issue List
- invalid/missing Issue ID handling
- Issue `404 Not Found` handling
- `401 Unauthorized` handling
- loading, empty, success, and error states where applicable
- Frontend delivery and regression tests
- focused API regression tests
- full Backend verification
- manual browser verification where practical

The relevant flow is:

```text
Issue List
   │
   ▼
Issue Detail
   │
   ├── Edit
   ├── Add Comment
   ├── Upload Attachment
   ├── Open Attachment
   └── Back
```

---

# Explicit Scope Boundary

This task implements the Issue Detail page only.

Do not implement:

- Issue Create UI
- Issue Edit UI itself
- Status editing on the Detail page
- Attachment deletion UI
- Comment edit/delete UI
- AI Draft UI
- Master Data UI
- Administration UI
- new Backend APIs
- new database behavior

The approved Issue Edit URL is:

```text
/issue-edit.html?issue_id={issue_id}
```

Implement navigation to this URL.

Do not implement `issue-edit.html`, a placeholder Issue Edit page, a temporary route, or alternate destination in this task.

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
- `docs/design/database_design.md`
- `docs/design/api_design.md`
- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/adr/ADR-001-user-in-control.md`
- `docs/adr/ADR-003-category-definition.md`
- `docs/adr/ADR-005-issue-as-aggregate-root.md`

Inspect the current implementation before changing code:

- `backend/app/main.py`
- `backend/app/api/routes/issues.py`
- `backend/app/api/routes/comments.py`
- `backend/app/api/routes/attachments.py`
- `backend/app/api/deps.py`
- `backend/app/schemas/issue.py`
- `backend/app/schemas/comment.py`
- `backend/app/schemas/attachment.py`
- `backend/tests/test_frontend.py`
- `backend/tests/test_main.py`
- `backend/tests/api/test_issues.py`
- existing Comment API tests
- existing Attachment API tests
- `frontend/issues.html`
- `frontend/css/style.css`
- `frontend/js/api.js`
- `frontend/js/auth.js`
- `frontend/js/issues.js`

Follow the actual repository structure if a listed path differs.

Reuse existing helpers, route patterns, error parsing, selected-Project state, logout behavior, and styling where appropriate.

Do not create duplicate fetch wrappers, authentication helpers, storage keys, route mounts, or competing UI conventions.

---

# Branch and Git Rules

Work only on:

```text
feature/issue-detail-ui
```

Before implementation, verify:

```bash
git branch --show-current
git status --short
git diff --check
```

Expected branch:

```text
feature/issue-detail-ui
```

Preserve existing user-authored changes when present, including:

- `docs/design/ui_design.md`
- `docs/design/detailed_design.md`
- `docs/design/test_design.md`
- `docs/implementation/feature-issue-detail-ui.md`

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

If the current branch differs, stop before editing.

If unrelated user changes are present, preserve them and report them.

---

# Documentation Policy

The approved design documents have already been updated for this task.

Do not modify Requirements, Design documents, ADRs, Project Conventions, `AGENTS.md`, or `CONTRIBUTING.md` unless the user explicitly approves another documentation change.

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
- existing shared Frontend modules
- existing FastAPI application
- existing Cookie-based Session authentication
- existing JSON REST APIs
- existing `sessionStorage` selected-Project behavior where needed
- native browser file input
- `FormData` for Attachment upload

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
├── issue.html
├── css/
│   └── style.css
└── js/
    ├── api.js
    ├── auth.js
    ├── login.js
    ├── projects.js
    ├── issues.js
    └── issue.js
```

Do not add Issue Create/Edit files or Node/tooling metadata.

---

# Browser URL

Implement:

|URL|Delivered file|
|---|---|
|`/issue.html`|`frontend/issue.html`|

The Issue ID is supplied by the query string:

```text
/issue.html?issue_id={issue_id}
```

The explicit Frontend route must use the existing FastAPI HTML-delivery pattern, return `frontend/issue.html`, use `include_in_schema=False`, and not depend on the current working directory.

Existing routes must remain unchanged. Do not add SPA fallback.

---

# Existing APIs

Use the existing APIs exactly as designed and implemented.

## Issue Detail

```http
GET /api/issues/{issue_id}
```

The response includes Issue, Project, ROOM/OTHER target data, Category, Description, Status, creator/updater data, timestamps, Comments, and Attachments.

Expected errors:

- `401 Unauthorized`
- `404 Not Found`

Do not change the Issue Detail API contract.

## Add Comment

```http
POST /api/issues/{issue_id}/comments
Content-Type: application/json
```

Request:

```json
{
  "comment": "Checked on site. Reproduced successfully."
}
```

Expected errors:

- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

Do not add a separate Comment page.

## Upload Attachment

```http
POST /api/issues/{issue_id}/attachments
Content-Type: multipart/form-data
```

Form field:

```text
file
```

Expected errors:

- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

Do not add a separate Attachment page.

## Open Attachment

Use:

```http
GET /api/attachments/{attachment_id}
```

The Backend returns the file with inline disposition when supported by the browser.

Do not invent a direct storage path or expose the storage directory.

---

# Issue ID Parsing and Validation

Read `issue_id` from `window.location.search` with `URLSearchParams` or equivalent browser-native parsing.

A usable Issue ID must be a positive integer.

Treat all of the following as invalid:

```text
/issue.html
/issue.html?issue_id=
/issue.html?issue_id=abc
/issue.html?issue_id=0
/issue.html?issue_id=-1
/issue.html?issue_id=1.5
```

When the Issue ID is missing or invalid:

1. do not call the Issue Detail API;
2. navigate to `/issues.html`.

Do not guess or silently choose an Issue ID.

---

# Initialization Flow

On `/issue.html?issue_id={issue_id}`:

1. parse and validate the Issue ID;
2. if invalid, navigate to `/issues.html`;
3. verify authentication using the existing approved Frontend/authentication pattern;
4. if authentication fails with `401`, clear selected Project state using the existing helper and navigate to `/`;
5. request `GET /api/issues/{issue_id}`;
6. if `404`, navigate to `/issues.html`;
7. render the Issue, Comments, and Attachments;
8. enable the page actions.

Do not trust browser storage as authentication proof. Do not render stale protected data after authentication failure. Avoid duplicate initialization requests.

---

# Current User and Project Context

Follow the existing common Header implementation and shared Frontend behavior.

Reuse current User and selected Project information when the existing implementation already provides it.

The Issue Detail API response is authoritative for the Issue's Project relationship.

Do not create a second selected-Project storage mechanism.

Do not silently rewrite stored Project information as a side effect of viewing an Issue.

If current User or Project context cannot be rendered without changing an approved API contract or inventing behavior, stop and report the conflict.

---

# Issue Detail HTML

`frontend/issue.html` must include semantic structure and stable IDs or data attributes for deterministic delivery tests.

Include at minimum:

- shared CSS
- `issue.js` loaded as an ES module
- page title
- common header area as supported by the existing Frontend
- Status
- Target Type
- Room display area
- Target display area
- Category
- Description
- Created By / Created At where supported by the existing API response
- Updated By / Updated At where supported by the existing API response
- Comments section
- Attachment section
- Edit action
- Add Comment action
- Upload Attachment action
- Back action
- loading state
- error/message area

Do not use inline event handlers. Do not add fields that are not supplied by approved APIs.

---

# Issue Rendering

Use safe DOM APIs such as `document.createElement()`, `textContent`, and explicit attribute assignment.

Do not interpolate API values into unsafe `innerHTML`.

## ROOM

For `target_type = ROOM`, display Room information and do not show an OTHER Target as though valid.

Example:

```text
Room: 1203
Target Type: ROOM
```

If Room data is unexpectedly missing, render a safe fallback without crashing. Do not infer a Room number from another field.

## OTHER

For `target_type = OTHER`, display Target and do not display a Room as though valid.

Example:

```text
Target Type: OTHER
Target: Network
```

If Target is unexpectedly missing, render a safe fallback without crashing.

## Unknown Target Type

Do not reinterpret unknown values as ROOM or OTHER. Show a safe generic fallback. Do not invent compatibility behavior for superseded Target Types.

## Status and Category

Display exact API values as text. Do not rely on color alone.

## Description

Render as plain text. Do not interpret Description as HTML.

## Timestamps

Use browser-native date/time formatting only. Handle malformed timestamps safely. Do not add date libraries.

---

# Comment List

Render the `comments` array returned by Issue Detail.

For each Comment display at minimum:

- comment text
- created-by display name when available
- created timestamp when available

Use plain-text rendering.

An empty Comments list is not an error. Show a clear empty state such as:

```text
コメントはありません。
```

Do not create demo Comments.

Do not fetch a separate Comment list during initial render unless the actual existing implementation requires it for a documented reason; the Issue Detail API already includes Comments.

---

# Add Comment

The Add Comment operation must remain inside the Issue Detail page.

Use a simple inline form/input area. Do not create another page or a modal framework.

A minimal flow is:

1. user activates `Add Comment`;
2. show or focus the Comment input area;
3. user enters Comment text;
4. submit to `POST /api/issues/{issue_id}/comments`;
5. prevent duplicate submission while the request is running;
6. on success, refresh authoritative Issue Detail data or otherwise update from approved API data;
7. show the newly registered Comment;
8. clear/reset the input as appropriate.

Do not fabricate Comment IDs or timestamps client-side.

If refreshing the entire Issue Detail after successful POST is the simplest way to obtain authoritative data, prefer that approach.

Prevent an obviously empty submission in the UI where practical, but do not bypass Backend validation.

For `400`, show a safe validation message and remain on the page.

For `404`, navigate to `/issues.html`.

For `401`, clear selected Project state using the existing helper and navigate to `/`.

Unexpected errors must not remove the user's entered Comment unless successful registration is confirmed.

---

# Attachment List

Render the `attachments` array returned by Issue Detail.

For each Attachment display fields supplied by the approved response that are useful for identification, such as:

- file name
- MIME type
- file size
- uploaded timestamp

Do not attempt to derive `original_file_name` if it is not present in the approved Issue Detail response.

An empty Attachment list is not an error. Show a clear empty state such as:

```text
添付ファイルはありません。
```

Do not create demo Attachments.

---

# Upload Attachment

The Upload Attachment operation must remain inside the Issue Detail page.

Use a native file input. Send exactly one selected file per request through `FormData` using field name `file`.

A minimal flow is:

1. user activates `Upload Attachment`;
2. show or focus the file selection area;
3. user selects a file;
4. submit to `POST /api/issues/{issue_id}/attachments`;
5. prevent duplicate submission while uploading;
6. on success, refresh authoritative Issue Detail data;
7. show the newly registered Attachment;
8. reset the file input as appropriate.

Do not duplicate Backend file validation rules in a way that can diverge from the API.

Browser `accept` may be used only as a usability hint if it matches approved supported media types; it must not replace Backend validation.

Do not read the file into base64 for the API. Do not put file contents into JSON.

For `400`, show a safe validation message and remain on the page.

For `404`, navigate to `/issues.html`.

For `401`, clear selected Project state using the existing helper and navigate to `/`.

For unexpected upload/network failure, show a safe error, preserve current page state, and do not claim success.

---

# Open Attachment

Each Attachment must provide an `Open Attachment` action using:

```text
/api/attachments/{attachment_id}
```

Do not construct paths from `file_name` or `file_path`. Do not expose Local Storage filesystem paths.

Use a normal browser navigation/opening mechanism compatible with Cookie-based Session authentication and the Backend's inline `Content-Disposition`.

Do not create a new custom Frontend download endpoint.

---

# Edit Navigation

The Edit action must navigate to:

```text
/issue-edit.html?issue_id={issue_id}
```

Use the validated Issue ID for the currently displayed Issue.

Do not implement the destination page in this task. Do not create a placeholder route to avoid the expected future `404`.

---

# Back Navigation

Back must navigate to:

```text
/issues.html
```

Do not rely exclusively on browser history because the approved destination is the Issue List.

Do not invent search-state restoration unless existing Frontend behavior already provides it.

---

# Authentication Handling

For protected API calls, `401 Unauthorized` means the Session is unusable.

On `401`:

1. stop protected rendering and pending UI success flow;
2. clear selected Project information through the existing shared helper;
3. navigate to `/`.

Apply this consistently to authentication/current-user checking, Issue Detail loading, Add Comment, and Upload Attachment.

Do not store authentication state in browser storage. Do not inspect or expose Session cookie values.

---

# `404` Handling

When Issue Detail, Comment creation, or Attachment upload proves the Issue is no longer available, navigate to:

```text
/issues.html
```

Clear stale Issue display before remaining on screen during any transition if necessary.

Do not invent a Not Found page.

---

# Error Handling Rules

Reuse existing shared API error handling where possible.

The Backend common error format is:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed."
  }
}
```

Frontend must not assume every error response contains valid JSON.

Handle safely:

- approved JSON error response
- empty response body
- malformed JSON
- network failure
- unexpected content type
- unexpected HTTP status

For unexpected failures, show a generic safe message such as:

```text
予期しないエラーが発生しました。
時間をおいて再度お試しください。
```

Do not expose internal exceptions, stack traces, filesystem paths, cookies, Session IDs, or raw request data.

---

# Loading and Duplicate-Action Handling

During initial loading, show a visible loading state and disable actions that depend on loaded Issue data.

During Comment submission, disable the relevant submission control and prevent duplicate Comment creation.

During Attachment upload, disable the relevant upload control and prevent duplicate uploads.

After a handled failure that does not navigate away, restore usable controls and preserve user input where practical.

Do not introduce complex cancellation infrastructure unless the current implementation actually needs it.

---

# CSS Requirements

Update `frontend/css/style.css` minimally and reuse existing styles before adding new ones.

Add only what is needed for:

- Issue Detail layout
- detail labels and values
- Description
- metadata/timestamps
- Comment list and form
- Attachment list and upload form
- action buttons/links
- loading state
- empty states
- error/success messages
- responsive/mobile layout

Maintain Mobile First, Simple UI, readable text, usable touch targets, visible focus, semantic controls, PC-browser usability, and offline operation.

Do not import external fonts, icons, CSS libraries, or scripts.

---

# Accessibility

Use semantic HTML first.

At minimum:

- associate labels with Comment/file controls;
- use actual buttons for actions;
- use links for navigation where appropriate;
- expose disabled states correctly;
- provide visible text labels;
- do not rely on color alone;
- keep keyboard focus visible;
- ensure dynamic messages are perceivable using the existing page pattern where practical.

Do not add unnecessary ARIA when native semantics are sufficient.

---

# Backend Change Limits

Expected Backend changes are limited to Frontend delivery and related tests.

Expected files may include:

- `backend/app/main.py`
- `backend/tests/test_frontend.py`
- `backend/tests/test_main.py`

Do not modify:

- Issue API contracts
- Comment API contracts
- Attachment API contracts
- Pydantic schemas
- Service methods
- Repository methods
- database models
- Alembic migrations
- database constraints
- authentication rules
- Session contents
- password handling
- error-response format
- Attachment storage behavior
- AI integration
- dependencies

No new runtime or development dependency is expected.

If implementation appears to require changing `backend/pyproject.toml` or `backend/uv.lock`, stop and report the reason before editing.

---

# FastAPI Delivery

Add explicit delivery for:

```http
GET /issue.html
```

using the existing HTML delivery pattern.

Requirements:

- return `frontend/issue.html`;
- set `include_in_schema=False`;
- keep static mounts unchanged unless a minimal approved change is actually needed;
- do not mount repository root;
- do not mount all Frontend content at `/`;
- do not add wildcard HTML routes;
- do not add SPA fallback.

The query string `issue_id` is consumed by browser JavaScript, not by a new Backend HTML route parameter.

---

# Required Automated Tests

Follow the current project test organization. Do not add a JavaScript test framework.

## HTML Delivery

Verify:

- `GET /issue.html` returns `200`;
- content type is HTML;
- Issue Detail page markers exist;
- shared `/css/style.css` is referenced;
- `/js/issue.js` is referenced;
- Detail fields/containers exist;
- Comments container exists;
- Attachments container exists;
- Edit, Add Comment, Upload Attachment, and Back controls exist;
- `/issue.html` is absent from OpenAPI.

## JavaScript Delivery

Verify:

- `GET /js/issue.js` returns `200`;
- content type is JavaScript-compatible;
- response is non-empty.

Extend existing JavaScript delivery tests rather than duplicating them when practical.

## Frontend Regression

Verify:

- `/` still serves Login;
- `/projects.html` still serves Project Selection;
- `/issues.html` still serves Issue List;
- unknown pages remain `404`;
- no SPA fallback exists;
- Frontend page routes remain absent from OpenAPI;
- existing static CSS/JavaScript delivery remains functional.

## API Regression

Run existing tests covering at minimum:

- `GET /api/issues/{issue_id}`
- `POST /api/issues/{issue_id}/comments`
- `POST /api/issues/{issue_id}/attachments`
- `GET /api/attachments/{attachment_id}`
- Authentication
- existing Frontend routes

Do not weaken existing tests merely to make new delivery pass.

---

# Manual Browser Verification

When practical, verify all of the following.

## Normal Detail Display

From Issue List, open a ROOM Issue and confirm Status, Room, Target Type, Category, Description, Comments, and Attachments.

Repeat with an OTHER Issue and confirm Target is shown instead of Room.

## Invalid Issue ID

Verify each redirects to `/issues.html` without an Issue API request:

```text
/issue.html
/issue.html?issue_id=
/issue.html?issue_id=abc
/issue.html?issue_id=0
```

## Not Found

Open a valid-form but nonexistent Issue ID and confirm redirect to `/issues.html`.

## Authentication Failure

With an expired/removed Session, opening Issue Detail must redirect to `/`, with selected Project state removed using existing behavior.

## Add Comment

- activate Add Comment;
- enter a valid Comment;
- submit;
- confirm success;
- confirm the new Comment appears;
- confirm duplicate submission is prevented.

Also verify a Backend validation error is displayed safely when practical.

## Upload Attachment

Using an approved small image or video test file:

- select the file;
- upload it;
- confirm success;
- confirm the Attachment appears;
- confirm duplicate upload is prevented.

Use project test data only. Do not upload sensitive personal files for testing.

## Open Attachment

Confirm the existing download endpoint is used and the browser can display/open the supported file as provided by the Backend.

## Navigation

- Edit goes to `/issue-edit.html?issue_id={id}`;
- the destination may return `404` because Issue Edit UI is intentionally not implemented in this task;
- Back goes to `/issues.html`.

Do not report the intentional Issue Edit destination `404` as a failure of this task.

Do not claim manual verification if it was not performed.

---

# Required Verification Commands

Before implementation, from repository root:

```bash
git branch --show-current
git status --short
git diff --check
```

Focused Frontend tests:

```bash
cd backend
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/test_frontend.py \
  tests/test_main.py
```

Issue regression:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/api/test_issues.py \
  tests/test_frontend.py \
  tests/test_main.py
```

Comment regression: run the actual existing Comment API test file(s).

Attachment regression: run the actual existing Attachment API test file(s).

Authentication regression:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q \
  tests/api/test_auth.py
```

Full Backend suite:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run pytest -s -q
```

Compile verification:

```bash
UV_CACHE_DIR=/tmp/cim-uv-cache uv run python -m compileall -q app tests
```

Final checks from repository root:

```bash
git diff --check
git status --short
git diff --stat
```

Inspect the actual modified files with `git diff -- ...`.

If an exact example test filename does not exist, use the actual existing test file that covers that API and report the command used.

---

# Existing TestClient Constraint

Previous tasks observed environment-specific FastAPI TestClient / AnyIO blocking in some sandbox executions.

If the same problem occurs:

1. confirm whether it reproduces in an existing unchanged test;
2. do not misreport it as an Issue Detail-specific failure;
3. use the already approved executable environment if available;
4. record the exact command and result;
5. do not claim a test passed if it only collected or timed out.

Do not silently skip the full suite.

---

# JavaScript Syntax Verification

Do not install Node.js.

If an existing JavaScript runtime is already available, syntax checking may be used.

If no JavaScript runtime is available, report that fact, perform static review, rely on FastAPI delivery tests, and perform manual browser verification where practical.

Do not modify project dependencies only to obtain a syntax checker.

---

# Self-Review Checklist

Before completion, review the entire diff.

Confirm:

## Scope

- only Issue Detail UI, delivery, minimal shared support, and related tests were implemented;
- Issue Create UI was not implemented;
- Issue Edit UI destination was not implemented;
- Attachment Delete UI was not implemented;
- no AI UI was added;
- no unrelated refactor was included;
- no Backend API contract changed;
- no database or migration changed;
- no dependency changed.

## Frontend Architecture

- `frontend/issue.html` exists;
- `frontend/js/issue.js` exists;
- shared CSS was changed minimally;
- shared `api.js` / `auth.js` helpers are reused;
- same-origin APIs are used;
- no duplicate fetch wrapper or auth storage exists;
- no build step exists.

## Issue ID

- query parameter is parsed safely;
- only positive integer IDs are accepted;
- invalid/missing ID redirects to `/issues.html`;
- invalid ID does not call the Issue API.

## Authentication

- Cookie-based Session is reused;
- `401` redirects to `/`;
- selected Project state is cleared through existing shared behavior;
- credentials/tokens are not stored;
- cookies are not manually exposed.

## Detail Rendering

- ROOM displays Room;
- OTHER displays Target;
- Target Type, Status, Category, and Description render safely;
- Comments and Attachments render from approved API data;
- API strings are not injected as HTML;
- malformed optional response data does not crash the page.

## Comment

- Comment is added through the approved API;
- empty obvious submissions are handled;
- duplicate submissions are prevented;
- successful state is refreshed from authoritative API data;
- `400`, `401`, and `404` are handled correctly;
- user input is not unnecessarily lost after unexpected failure.

## Attachment

- Upload uses `FormData`;
- field name is exactly `file`;
- no base64/JSON file upload is used;
- successful state is refreshed from authoritative API data;
- Open Attachment uses `/api/attachments/{attachment_id}`;
- Local Storage paths are never exposed;
- duplicate uploads are prevented;
- `400`, `401`, and `404` are handled correctly.

## Navigation

- Edit uses `/issue-edit.html?issue_id={issue_id}`;
- no Issue Edit placeholder exists;
- Back uses `/issues.html`;
- Issue `404` redirects to `/issues.html`.

## Delivery and Tests

- `/issue.html` is delivered;
- `/issue.html` is excluded from OpenAPI;
- previous Frontend routes still work;
- unknown routes remain `404`;
- no SPA fallback exists;
- API routes remain reachable;
- focused tests pass;
- API regressions pass;
- full suite passes;
- compile verification passes;
- `git diff --check` passes;
- manual browser testing is reported accurately.

---

# Stop Conditions

Stop immediately and report before continuing if any of the following occurs:

- current branch is not `feature/issue-detail-ui`;
- user-authored changes would be overwritten;
- latest approved documents conflict on Issue Detail behavior;
- Issue Edit navigation is required but the approved URL differs from `/issue-edit.html?issue_id={issue_id}`;
- Comment or Attachment UI requires an undocumented API;
- the existing Issue Detail response is insufficient to implement an approved required display item;
- a new API/schema/Service/Repository/DB change appears necessary;
- a new dependency or Node tooling appears necessary;
- existing shared Frontend modules would require redesign rather than a minimal reusable change;
- `/issue.html` cannot be added safely using the existing explicit delivery pattern;
- implementation requires exposing storage paths;
- design documents need another update;
- unrelated cleanup becomes necessary.

When stopping, report the exact conflict/blocker, affected files/documents and sections, commands/tests already run, files modified so far, minimum decision needed, and remaining work.

Do not resolve a Stop Condition by assumption.

---

# Completion Report

Use exactly these headings:

## Summary

## Modified Files

Separate implementation, tests, and preserved user documentation. List every modified or added file.

## Tests

Include commands executed, pass/fail counts, warnings, failed attempts, TestClient/sandbox behavior if encountered, JavaScript verification, and manual browser verification status.

Do not claim unexecuted tests passed.

## Design Compliance

Confirm at minimum:

- HTML + CSS + JavaScript only;
- no npm/build tool;
- existing JSON APIs reused;
- existing Cookie Session reused;
- Issue ID validation implemented;
- ROOM / OTHER rendering implemented;
- Comment list and Add Comment implemented;
- Attachment list, Upload, and Open implemented;
- invalid Issue ID handling implemented;
- Issue `404` handling implemented;
- `401` handling implemented;
- Edit uses the approved URL;
- Back returns to Issue List;
- safe DOM rendering used;
- OpenAPI unchanged except intentional non-schema Frontend route;
- no API/DB/migration/dependency changes;
- Issue Edit/Create remain out of scope.

## Assumptions

Use:

```text
None.
```

unless a genuine permitted assumption was necessary.

## Remaining Work

Expected at minimum:

```text
Issue Create UI and Issue Edit UI remain for later tasks.
```

Report any additional real remaining work accurately.

---

# Completion Criteria

Do not mark this task complete until all applicable items below are satisfied:

- correct branch is used;
- user-authored document changes are preserved;
- `frontend/issue.html` is added;
- `frontend/js/issue.js` is added;
- shared CSS is updated minimally;
- `/issue.html` delivery is added;
- `/issue.html` is excluded from OpenAPI;
- valid `issue_id` parsing is implemented;
- invalid/missing Issue ID redirects to `/issues.html` without API fetch;
- Issue Detail is loaded from the existing API;
- ROOM and OTHER render correctly;
- Status, Category, Description, and available metadata render safely;
- Comment list is rendered;
- empty Comment state works;
- Add Comment works through the existing API;
- duplicate Comment submission is prevented;
- Attachment list is rendered;
- empty Attachment state works;
- Upload Attachment works through the existing API;
- duplicate Attachment upload is prevented;
- Open Attachment uses the existing Attachment download API;
- Issue `404` redirects to `/issues.html`;
- `401` redirects to Login using existing shared behavior;
- Edit navigates to the approved Issue Edit URL;
- Back navigates to Issue List;
- loading and errors are visible;
- no unsafe API-data HTML injection is introduced;
- no React/TypeScript/npm/build tools are introduced;
- no new dependency is introduced;
- no API/schema/Service/Repository/model/migration change is introduced;
- no Issue Edit/Create destination page is added;
- focused tests pass;
- relevant API regression tests pass;
- full Backend suite passes;
- compile verification passes;
- `git diff --check` passes;
- full diff is reviewed;
- manual browser verification is completed where practical and reported honestly;
- no commit, push, Pull Request, or merge is performed.

Do not mark complete if required verification fails or unapproved changes were added.
