# Database Models Implementation Guide

## Feature

`feature/database-models`

------------------------------------------------------------------------

## Purpose

Implement the database layer for the Commissioning Issue Manager (CIM).

This feature establishes the SQLAlchemy models, relationships,
constraints, indexes, and the Alembic migration extending the existing migration history.

Business logic must **not** be implemented in this feature.

------------------------------------------------------------------------

## Read First

Review the following before implementation:

-   AGENTS.md
-   CONTRIBUTING.md
-   requirements.md
-   basic_design.md
-   database_design.md
-   api_design.md
-   detailed_design.md
-   test_design.md
-   project_conventions.md
-   ADRs

Latest design documents always take precedence over ADRs.

------------------------------------------------------------------------

## Scope

Implement only:

-   SQLAlchemy models
-   Enums
-   Relationships
-   Constraints
-   Indexes
-   Alembic migration extending the existing migration history
-   Model tests
-   Migration tests

------------------------------------------------------------------------

## Models

Implement:

-   User
-   Hotel
-   Project
-   RoomType
-   Room
-   Issue
-   Comment
-   Attachment

Use SQLAlchemy 2.x typed ORM.

------------------------------------------------------------------------

## Enum

Implement only the values defined by the latest design.

-   Role
-   TargetType
-   Category
-   Status

Do not introduce undocumented values.

------------------------------------------------------------------------

## Database Requirements

Implement:

-   Primary Keys
-   Foreign Keys
-   Required Unique Constraints
-   Required Check Constraints
-   Required Indexes

Do not introduce undocumented columns or constraints.

------------------------------------------------------------------------

## Relationships

Implement relationships according to the latest database design.

Use `back_populates` where appropriate.

Avoid unnecessary cascade rules.

Do not implement business validation inside models.

------------------------------------------------------------------------

## Existing Code

Review existing models before modifying them.

If `app/db/database.py` still exists, verify all references before
removal.

Example:

``` bash
grep -R "app\.db\.database\|db\.database" -n backend/app backend/tests
```

Remove the compatibility module only after every reference has been
migrated.

------------------------------------------------------------------------

## Alembic

Preserve the existing Alembic migration history.

Do not delete, squash, replace, or rewrite the existing migration files.

Create a new migration after the current head to align the existing schema with the latest database design.

Verify the complete migration chain using a temporary SQLite database:

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
```

Also verify that a new empty temporary SQLite database can be upgraded from base to head:

```bash
uv run alembic upgrade head
```

Do not modify the production database.

------------------------------------------------------------------------

## Testing

Run:

``` bash
uv run pytest
```

Verify at minimum:

-   metadata registration
-   foreign keys
-   unique constraints
-   enum persistence
-   relationships
-   migration upgrade
-   migration downgrade

Do not modify the production database.

------------------------------------------------------------------------

## Dependencies

Only add Alembic if it is not already configured.

Do not upgrade unrelated dependencies.

Do not introduce Ruff, mypy, Docker, or other tooling.

------------------------------------------------------------------------

## Git Rules

-   Work only on `feature/database-models`
-   Do not commit
-   Do not push
-   Do not create a Pull Request

------------------------------------------------------------------------

## Acceptance Criteria

-   All models implemented
-   Relationships implemented
-   Constraints implemented
-   Indexes implemented
-   Migration extending the existing migration history implemented
-   Upgrade succeeds
-   Downgrade succeeds
-   Tests pass
-   No business logic added
-   No unnecessary files included

------------------------------------------------------------------------

## Completion Report

Report using the following structure.

### Summary

### Modified Files

### Models

### Relationships

### Constraints and Indexes

### Migration

### Tests

Executed commands and results.

### Design Compliance

Confirm compliance with the latest design documents.

### Remaining Work

Describe the next feature.

------------------------------------------------------------------------

## Notes

This feature only establishes the persistence layer.

Repositories, Services, APIs, Authentication, AI integration, and
application workflows are intentionally out of scope.
