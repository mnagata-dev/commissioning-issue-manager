# CIM (Commissioning Issue Manager)

## Overview

CIM (Commissioning Issue Manager) は、Lutron照明制御システムのコミッショニング業務において発生するIssueを効率的に管理するためのWebアプリケーションです。

コミッショニング現場では、IssueをExcelやMicrosoft Teamsなどで管理することが多く、情報の分散や入力負荷が課題となっています。

CIMはこれらの課題を解決し、現場でのIssue管理をシンプルかつ効率的に行うことを目的としています。

---

# Goals

本プロジェクトの目的は以下のとおりです。

* コミッショニングIssueをProject単位で管理する。
* スマートフォンから素早くIssueを登録する。
* 写真・動画をIssueへ添付する。
* AI（Ollama）を利用してIssue入力を支援する。
* 将来的にUbuntu Serverへ移行可能な設計とする。
* 保守しやすく拡張しやすいシステムを構築する。

---

# Features (Initial Version)

初期版では以下の機能を提供します。

* User Authentication
* Project Selection
* Issue Management
* Comment Management
* Attachment Management
* AI Draft Generation
* Local File Storage
* Administration（CLI / CSV）

---

# Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* SQLite

## Frontend

* React
* TypeScript

## AI

* Ollama
* Local LLM

## Development Environment

* Windows 11
* WSL2 Ubuntu LTS
* Visual Studio Code

---

# Project Structure

```text
cim/
├── backend/
├── frontend/
├── storage/
├── scripts/
├── tests/
├── docs/
│   ├── requirements/
│   ├── design/
│   └── adr/
├── README.md
├── LICENSE
└── .gitignore
```

---

# Documentation

## Requirements

* `docs/requirements/requirements.md`

## Design

* `docs/design/basic_design.md`
* `docs/design/database_design.md`
* `docs/design/api_design.md`
* `docs/design/ui_design.md`
* `docs/design/detailed_design.md`
* `docs/design/test_design.md`

## Architecture Decision Records

* `docs/adr/ADR-001-user-in-control.md`
* `docs/adr/ADR-002-target-type-definition.md`
* `docs/adr/ADR-003-category-definition.md`
* `docs/adr/ADR-004-room-model-design.md`
* `docs/adr/ADR-005-issue-as-aggregate-root.md`

---

# Development Policy

本プロジェクトでは以下の設計方針を採用しています。

* Documentation First
* User in Control
* Business First
* API First
* Layered Architecture
* Repository Pattern
* Service Layer Pattern

詳細は `docs/project_conventions.md` を参照してください。

---

# Current Status

現在は設計フェーズが完了し、実装フェーズへ移行する段階です。

完成済みドキュメント

* Requirements Specification
* Basic Design
* Database Design
* API Design
* UI Design
* Detailed Design
* Test Design
* Architecture Decision Records

---

# Future Roadmap

今後の開発予定

1. Backend実装
2. Database実装
3. AI Integration
4. Frontend実装
5. Test実装
6. Docker対応
7. Ubuntu Server対応

---

# License

This project is licensed under the MIT License.
