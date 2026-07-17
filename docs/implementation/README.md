# Implementation Guides

## Purpose

This directory contains implementation guides for individual features of the Commissioning Issue Manager (CIM).

Each guide is intended to be used as the implementation instruction for Codex (or another coding AI) when implementing a single feature.

One guide corresponds to one feature branch and one Pull Request.

---

## Goals

The implementation guides aim to:

- keep each implementation small and reviewable
- ensure implementation follows the latest design documents
- provide clear implementation boundaries
- reduce ambiguity during implementation
- standardize implementation instructions across the project

---

## Relationship with Other Documents

Implementation guides do **not** replace the project documentation.

The following documents remain the Source of Truth.

1. `requirements.md`
2. Design documents
   - `basic_design.md`
   - `database_design.md`
   - `api_design.md`
   - `ui_design.md`
   - `detailed_design.md`
   - `test_design.md`
3. `project_conventions.md`
4. ADR
5. `review_notes.md`
6. `CHANGELOG.md`

If an implementation guide conflicts with the latest design documents, the latest design documents take precedence.

---

## Prerequisites

Before starting implementation, always review:

- `AGENTS.md`
- `CONTRIBUTING.md`
- the latest project documentation
- the implementation guide for the target feature

---

## One Feature = One Guide

Each implementation guide corresponds to a single feature.

Examples:

```
feature-backend-foundation.md
feature-database-models.md
feature-repositories.md
feature-services.md
feature-issue-create.md
```

A guide should never include multiple independent features.

---

## Standard Workflow

The expected workflow is:

1. Read the implementation guide.
2. Review the latest design documents.
3. Implement the feature.
4. Create or update tests.
5. Perform self-review.
6. Submit the implementation for ChatGPT review.
7. Commit.
8. Create a Pull Request.
9. Merge after review.

---

## Guide Template

All implementation guides should be created from:

```
implementation-guide-template.md
```

This keeps every guide consistent across the project.

---

## Scope

Implementation guides should describe only feature-specific requirements.

Do not duplicate:

- AGENTS.md
- CONTRIBUTING.md
- project conventions
- design documents

Instead, reference them where appropriate.

---

## Naming Convention

Use the following naming convention:

```
feature-<feature-name>.md
```

Examples:

```
feature-backend-foundation.md
feature-database-models.md
feature-room-api.md
feature-issue-create.md
```

---

## Maintenance

Implementation guides should be updated when:

- implementation scope changes
- the related design changes
- implementation feedback improves the guide

Historical implementation guides should be kept whenever they accurately describe merged work.
