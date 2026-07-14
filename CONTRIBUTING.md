# Contributing

Thank you for contributing to the Commissioning Issue Manager (CIM) project.

This document defines the development workflow, coding rules, review process, and AI usage guidelines for this project.

---

# 1. Purpose

This project follows a **design-first development process**.

Implementation must follow the approved design documents.

If implementation requires a design change, update the design first after discussion and agreement.

---

# 2. Document Priority

Use the following priority when making implementation decisions.

1. `requirements.md`
2. Design documents
   - `basic_design.md`
   - `database_design.md`
   - `api_design.md`
   - `ui_design.md`
   - `detailed_design.md`
   - `test_design.md`
3. `project_conventions.md`
4. ADR (Architecture Decision Records)
5. `review_notes.md`
6. `CHANGELOG.md`

The latest version of the Requirements and design documents always takes precedence.

ADR documents describe the background and rationale for design decisions.

If an ADR conflicts with the latest design documents, follow the latest design documents.

---

# 3. Development Principle

Design documents are the source of truth.

AI tools should assist implementation, not redefine the design.

When implementation and design conflict:

- Do not change the implementation to match assumptions.
- Do not modify the design without agreement.
- Discuss the issue first.
- Update the design documents if necessary.
- Implement only after the design has been agreed.

---

# 4. Development Workflow

Develop each feature in small increments.

One feature should correspond to:

- One branch
- One Pull Request

Recommended workflow:

1. Confirm the design
2. Implement
3. Write tests
4. Review
5. Commit
6. Create Pull Request
7. Merge

---

# 5. Branch Strategy

Use the following branch naming conventions.

| Purpose | Example |
| --- | --- |
| Feature | `feature/issue-api` |
| Bug Fix | `fix/login-validation` |
| Documentation | `docs/update-api-design` |
| Refactoring | `refactor/service-layer` |
| Test | `test/issue-service` |

---

# 6. Commit Convention

Follow Conventional Commits.

Examples:

```text
feat(issue): implement issue repository

fix(auth): validate username

docs(api): update create issue request

refactor(service): simplify validation logic

test(issue): add issue service tests
```

---

# 7. Pull Request

Keep Pull Requests small and easy to review.

Each Pull Request should:

- implement one feature
- update related documents if necessary
- include appropriate tests
- follow project conventions
- avoid unrelated changes

---

# 8. Design Rules

- Requirements are the highest priority.
- Do not implement undocumented features.
- Do not guess missing specifications.
- If the design is unclear, ask before implementation.
- If a design change is required, propose it first.
- Implement only after the design has been updated and agreed.

---

# 9. Coding Rules

Follow the rules defined in `project_conventions.md`.

In particular:

- directory structure
- naming conventions
- coding style
- API naming
- Markdown style

---

# 10. Testing

Tests should follow `test_design.md`.

Implementation is not complete until the corresponding tests have been added.

Prefer automated tests whenever practical.

---

# 11. Review Rules

Before implementation:

- Verify consistency with all design documents.

After implementation:

- Verify consistency with:
  - Requirements
  - Design documents
  - Test Design
  - Project Conventions

If improvements require design changes, propose them before implementation.

---

# 12. AI Instructions

This project actively uses AI-assisted development.

## ChatGPT

Use ChatGPT for:

- implementation planning
- architecture discussions
- design review
- code review
- refactoring advice
- debugging
- Git / GitHub workflow support

## Codex

Use Codex for:

- code implementation
- file creation and editing
- test implementation
- refactoring
- repetitive development tasks

---

# 13. AI Development Rules

When using AI:

1. Read the latest project documents before implementation.
2. Follow the document priority defined in this file.
3. Never modify the design without prior agreement.
4. Never implement undocumented requirements.
5. If requirements or design documents are inconsistent, report the issue and wait for clarification before implementation.
6. Keep implementations small and reviewable.
7. Do not sacrifice readability or maintainability for unnecessary optimization.

---

# 14. References

- `requirements.md`
- `basic_design.md`
- `database_design.md`
- `api_design.md`
- `ui_design.md`
- `detailed_design.md`
- `test_design.md`
- `project_conventions.md`
- `review_notes.md`
- `CHANGELOG.md`
- `docs/adr/*`

---

End of Document
