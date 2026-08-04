# Comment API Implementation Guide

This document is intended to be stored as
`docs/implementation/feature-comment-api.md`.

## Purpose

Implement the Comment API according to the approved design documents.

## Source of Truth

1.  requirements.md
2.  basic_design.md
3.  database_design.md
4.  api_design.md
5.  ui_design.md
6.  detailed_design.md
7.  test_design.md
8.  project_conventions.md
9.  ADR-001 -- ADR-005
10. AGENTS.md

If documents conflict or required behavior is undefined, stop and report
the issue.

## Branch

`feature/comment-api`

Do not commit, push, create a Pull Request, or merge.

## Scope

Implement only:

-   POST /api/issues/{issue_id}/comments
-   GET /api/issues/{issue_id}/comments

Include Router, Service, Dependency wiring, DTO conversion, and tests.

Do not modify Authentication, Attachment API, AI Draft API, Frontend,
Database schema, or Migrations.

## Architecture Rules

-   Router calls Service only.
-   Repository performs persistence only.
-   Service owns business logic and transactions.
-   GET operations must not commit or rollback.

## Validation

Validate according to the design:

-   Issue exists
-   User exists
-   Request is valid

## Testing

Implement API tests and Service tests covering success and error cases.

## Stop Conditions

Stop if the design is ambiguous. Do not guess.

## Completion Report

Return:

-   Summary
-   Modified Files
-   Tests
-   Design Compliance
-   Assumptions
-   Remaining Work
