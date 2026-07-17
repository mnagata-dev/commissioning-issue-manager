# Codex Implementation Guide Template

> This document defines the implementation instructions for a single feature.
>
> Read this document together with:
>
> - `AGENTS.md`
> - `CONTRIBUTING.md`
> - Latest design documents

---

# Feature

```
feature/<feature-name>
```

---

# Purpose

Describe the purpose of this feature.

---

# Read First

Before implementation, review the following documents.

Priority:

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

If ADRs conflict with the latest design documents, the latest design documents take precedence.

---

# Scope

Describe what should be implemented.

Example:

- SQLAlchemy Models
- Repository
- API
- Service
- Tests

---

# Implementation Requirements

Describe all implementation requirements.

Include only feature-specific requirements.

Do not repeat AGENTS.md.

---

# Existing Code

Describe existing implementation that must be considered.

Examples:

- Existing Models
- Existing API
- Existing Tests

---

# Out of Scope

Describe what must NOT be implemented.

---

# Dependencies

Describe dependency changes if necessary.

Otherwise:

> Do not update dependencies.

---

# Testing

Describe required tests.

Examples:

- Unit Tests
- API Tests
- Migration Tests

List required commands.

```bash
uv run pytest
```

---

# Git Rules

- Do not commit
- Do not push
- Do not create a Pull Request

---

# Acceptance Criteria

Describe when this feature is considered complete.

Examples:

- Tests pass
- Design compliance
- No unnecessary files
- No undocumented behavior

---

# Completion Report

Report using the following format.

## Summary

...

## Modified Files

...

## Design Compliance

...

## Tests

...

## Remaining Work

...
