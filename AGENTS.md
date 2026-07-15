# AGENTS.md

# Commissioning Issue Manager (CIM)

This document defines the implementation rules for AI coding agents working on the Commissioning Issue Manager (CIM) project.

All implementations must follow the approved project documents and architecture.

---

# Project Overview

## Project Name

Commissioning Issue Manager (CIM)

## Purpose

A web application for managing commissioning issues during Lutron system commissioning.

The application allows engineers to register, update, search, and manage Issues while using AI only as an input assistant.

---

# Technology Stack

## Backend

- FastAPI
- SQLAlchemy
- Alembic

## Frontend

- HTML
- JavaScript

## Database

- SQLite

## AI

- Ollama

## Development Environment

- Windows 11
- WSL2 Ubuntu
- VS Code

---

# Source of Truth

Always follow the project documents in the following priority.

1. requirements.md
2. basic_design.md
3. database_design.md
4. api_design.md
5. ui_design.md
6. detailed_design.md
7. test_design.md
8. project_conventions.md
9. ADR-001 ～ ADR-005
10. CONTRIBUTING.md
11. review_notes.md
12. CHANGELOG.md

The document categories have different purposes.

- Requirements define what the system must do.
- Design documents define how the system should be implemented.
- ADRs record why important architectural decisions were made.
- CONTRIBUTING.md defines development workflow and collaboration rules.
- Review Notes record review history.
- CHANGELOG records project history.

If documents conflict:

- Never guess.
- Follow the higher-priority document.
- Report the inconsistency.
- Do not silently change the implementation.

---

# Development Principles

Follow these principles throughout implementation.

- Documentation First
- User in Control
- Business First
- Layered Architecture
- API First
- Repository Pattern
- Service Layer Pattern
- Issue is the Aggregate Root
- Simplicity over complexity
- Readability over cleverness
- Consistency over personal preference

---

# Architecture Rules

The project uses Layered Architecture.

Responsibilities must remain separated.

## API

Responsible for:

- HTTP request handling
- Dependency Injection
- Request / Response conversion

Must NOT contain:

- Business logic
- Database queries

## Service

Responsible for:

- Business rules
- Validation
- Transaction management
- Coordination between components

## Repository

Responsible for:

- Database access only

Must NOT contain:

- Validation
- Business rules

## Models

- SQLAlchemy models

## Schemas

- Pydantic DTOs

## Core

- Configuration
- Security
- Shared utilities

---

# Domain Rules

Issue is the Aggregate Root.

Comment and Attachment always belong to Issue.

AI never creates or updates business data.

AI only generates:

- Category
- Description

AI must never determine:

- Room
- Target Type
- Target

The final decision always belongs to the user.

---

# Implementation Rules

## Do

- Follow all approved designs.
- Keep implementations simple.
- Use existing coding style.
- Use type hints.
- Keep functions focused on a single responsibility.
- Write maintainable code.
- Reuse existing code when appropriate.
- Keep changes minimal.
- Update tests when behavior changes.

## Do NOT

- Add undocumented features.
- Change architecture.
- Change database schema.
- Change API contracts.
- Rename files unnecessarily.
- Modify design documents.
- Modify ADRs.
- Modify project conventions.
- Introduce unrelated refactoring.

Unless explicitly instructed.

---

# Branch Rules

- Work only on the assigned branch.
- Never merge branches.
- Never rewrite Git history.
- Never force push.
- Never modify unrelated files.

---

# Commit Guidelines

Commits should be:

- Small
- Focused
- Atomic

Each commit should implement a single logical change.

Avoid combining unrelated changes.

---

# Code Style

Prefer:

- Clear variable names
- Small functions
- Explicit logic
- Readability

Avoid:

- Clever tricks
- Deep nesting
- Magic numbers
- Duplicate logic

Prefer constants and enums.

Raise project-specific exceptions where appropriate.

Return user-friendly error messages.

---

# Backend Structure

Follow the directory structure defined in detailed_design.md.

## app/api/

- HTTP endpoints

## app/services/

- Business logic

## app/repositories/

- Database access

## app/models/

- SQLAlchemy models

## app/schemas/

- Pydantic DTOs

## app/core/

- Configuration
- Security
- Shared components

---

# Testing

Before considering a task complete:

Run:

- Unit Tests
- Service Tests
- Repository Tests
- API Tests

when applicable.

Typical command:

```bash
uv run pytest
```

If tests cannot be executed:

- Explain why.

Never claim code works without verification.

---

# Deliverables

When finishing a task, always report:

## Summary

- What was implemented.

## Modified Files

- List every modified file.

## Tests

- What was executed.
- What passed.
- What was not executed.

## Assumptions

- Any assumptions made.

## Remaining Work

- Any known limitations.

Never claim unfinished work is complete.

---

# Pull Request Checklist

Before creating a Pull Request, confirm:

- Requirements followed.
- Design followed.
- No architecture changes.
- No unrelated changes.
- Tests updated.
- Existing tests pass.
- Documentation unchanged unless requested.

---

# Decision Policy

When multiple implementation choices exist, choose:

1. Simpler implementation.
2. Existing project style.
3. Easier maintenance.
4. Lower risk.

Never optimize prematurely.

---

# AI Agent Behavior

When uncertain:

- Ask for clarification instead of guessing.

When documents conflict:

- Report the conflict.

When implementation differs from the design:

- Follow the design.

When discovering a better design:

- Do NOT implement it automatically.

Suggest it separately.

---

# AI Agent Scope

The AI agent is an implementation assistant.

The AI agent must not:

- Invent new requirements.
- Redesign the architecture.
- Change APIs without approval.
- Modify the database design without approval.
- Modify requirements or design documents unless explicitly instructed.

If improvements are found:

1. Implement only the requested work.
2. Report the suggested improvement separately.
3. Wait for user approval before applying it.

---

# Document Update Policy

Implementation must never become the source of truth.

If implementation reveals a problem in the documentation:

- Do not modify the documentation automatically.
- Report the inconsistency.
- Suggest the required document updates.
- Wait for user approval before changing any project document.

---

# Project Philosophy

The project prioritizes:

- Correctness
- Maintainability
- Consistency
- Simplicity

over:

- Cleverness
- Premature optimization
- Personal coding style

Every implementation should make the project easier to understand for future developers.
