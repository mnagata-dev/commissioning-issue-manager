# Backend Foundation Implementation Guide

## Feature

`feature/backend-foundation`

------------------------------------------------------------------------

## Purpose

Implement the backend foundation required for future CIM development.

This feature establishes the application infrastructure only. Business
features must **not** be implemented.

------------------------------------------------------------------------

## Read First

Before implementation, review:

-   AGENTS.md
-   CONTRIBUTING.md
-   requirements.md
-   basic_design.md
-   database_design.md
-   api_design.md
-   ui_design.md
-   detailed_design.md
-   test_design.md
-   project_conventions.md
-   ADRs

Latest design documents take precedence over ADRs.

------------------------------------------------------------------------

## Scope

Implement:

-   FastAPI application factory
-   Configuration management
-   Common application exceptions
-   SQLAlchemy Base
-   Database session management
-   API dependency module
-   Backend package structure
-   Foundation tests

------------------------------------------------------------------------

## Out of Scope

Do NOT implement:

-   Models
-   Repository
-   Service
-   API endpoints
-   Authentication
-   Alembic
-   AI
-   Frontend
-   Business logic

------------------------------------------------------------------------

## Implementation Requirements

### Application

Implement an application factory.

Example:

``` python
def create_app() -> FastAPI:
    ...
```

Do not implement business routers.

### Configuration

Create a centralized Settings object.

Use environment variables.

Keep configuration minimal.

### Database

Implement:

-   Declarative Base
-   Engine
-   SessionLocal
-   Dependency for DB Session

Do not call `Base.metadata.create_all()`.

### Exceptions

Implement:

-   ApplicationError
-   Common exception handler

Do not implement feature-specific exceptions.

### Package Structure

    backend/app/
        api/
        core/
        db/
        repositories/
        schemas/
        services/

Create only the minimum package structure required.

### Existing Code

Reuse existing code whenever appropriate.

Avoid unnecessary rewrites.

If an existing file is replaced, explain why.

------------------------------------------------------------------------

## Testing

Run:

``` bash
uv run pytest
```

Tests should verify:

-   application factory
-   configuration
-   database session
-   exception handler

Do not modify the production database.

------------------------------------------------------------------------

## Dependencies

Only add dependencies required for the backend foundation.

Do not upgrade unrelated packages.

------------------------------------------------------------------------

## Git Rules

-   Work only on `feature/backend-foundation`
-   Do not commit
-   Do not push
-   Do not create a Pull Request

------------------------------------------------------------------------

## Acceptance Criteria

-   Application factory implemented
-   Configuration implemented
-   Database session implemented
-   Declarative Base implemented
-   Exception handling implemented
-   Tests added
-   Existing tests pass
-   No business functionality added
-   No unnecessary files included

------------------------------------------------------------------------

## Completion Report

Use the following format.

### Summary

Brief summary.

### Modified Files

List all modified files.

### Tests

Executed commands.

Example:

``` bash
uv run pytest
```

Include the result.

### Design Compliance

Confirm compliance with the latest design documents.

### Remaining Work

Describe the next feature to implement.

------------------------------------------------------------------------

## Notes

This guide intentionally establishes only the project foundation.

Future features such as database models, repositories, services, APIs,
authentication, and AI integration will be implemented in separate
feature branches.
