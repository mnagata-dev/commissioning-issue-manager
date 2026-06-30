# CIM Project Conventions

**Document Version:** 1.0
**Status:** Active
**Last Updated:** 2026-06-30
**Author:** Masato Nagata

---

# Revision History

| Version | Date       | Description     |
| ------- | ---------- | --------------- |
| 1.0     | 2026-06-30 | Initial version |

---

# Table of Contents

1. Purpose
2. Project Principles
3. Documentation Rules
4. Documentation Language
5. Markdown Rules
6. Naming Conventions
7. Directory Structure
8. Git Workflow
9. Branch Naming
10. Commit Message
11. ADR Rules
12. Design Rules
13. Coding Rules
14. AI Collaboration
15. Versioning Rules
16. Development Environment
17. Review Policy

---

# 1. Purpose

本ドキュメントは、CIM（Commissioning Issue Manager）プロジェクトにおける共通ルールを定義する。

要件定義、設計、実装、テスト、運用まで、一貫した品質を維持することを目的とする。

本プロジェクトへ新たなドキュメントやソースコードを追加する場合は、本ドキュメントのルールに従う。

---

# 2. Project Principles

CIMでは以下の設計原則を採用する。

1. Keep Things Simple
2. User in Control
3. Business First
4. Documentation First
5. Layered Architecture
6. Single Responsibility Principle
7. Repository Pattern
8. Service Layer Pattern
9. API First
10. Master Data First
11. Validation in Service Layer

新しい設計判断を行う場合は、これらの原則との整合性を確認する。

---

# 3. Documentation Rules

## 3.1 Documentation Structure

```text
docs/
├── README.md
├── project_conventions.md
├── requirements/
├── design/
├── adr/
└── images/
```

---

## 3.2 Document Roles

| ドキュメント              | 役割             |
| ------------------- | -------------- |
| README              | docs全体の案内      |
| Project Conventions | プロジェクト全体の共通ルール |
| Requirements        | 要件定義           |
| Design              | 設計書            |
| ADR                 | 設計判断の記録        |
| Images              | 図・画像           |

---

## 3.3 Documentation Policy

* ドキュメントを先に作成し、その後に実装を行う。
* 設計変更時はドキュメントを先に更新する。
* ドキュメントはGitで管理する。
* Markdown形式を採用する。

---

# 4. Documentation Language

## 4.1 基本方針

本文は日本語で記述する。

コード・API・クラス名・ドメインモデルは英語表記を採用する。

---

## 4.2 ドメイン名

以下は英語表記とする。

* User
* Hotel
* Project
* RoomType
* Room
* Issue
* Comment
* Attachment

---

## 4.3 機能名

以下は英語表記とする。

* Authentication
* Project Management
* Issue Management
* AI Draft
* Comment Management
* Attachment Management

---

## 4.4 Source Code Language

ソースコード中の識別子は英語で記述する。

識別子には以下を含む。

* クラス名
* 関数名
* メソッド名
* 変数名
* 定数名
* ファイル名
* ディレクトリ名
* APIエンドポイント
* JSONキー
* データベースのテーブル名
* データベースのカラム名

日本語のローマ字表記は使用しない。

例：

| 良い例                | 悪い例                 |
| ------------------ | ------------------- |
| `room_id`          | `heya_id`           |
| `lighting`         | `shoumei`           |
| `issue_service.py` | `mondai_service.py` |
| `created_at`       | `sakusei_bi`        |

コードコメントおよびdocstringは原則として英語で記述する。

ただし、設計意図や業務知識など、日本語で記述した方が理解しやすい場合は、日本語のコメントを認める。

ユーザー向け表示文言は、UIの言語方針に従う。

---

## 4.5 表

表の見出しは日本語を基本とする。

例

| 機能             | 説明     |
| -------------- | ------ |
| Authentication | ユーザー認証 |

---

# 5. Markdown Rules

## 見出し

以下のレベルを使用する。

```text
#
##
###
```

---

## 箇条書き

ハイフン（-）を使用する。

---

## コード

コードブロックを使用する。

言語指定を行う。

例

```python
def hello():
    print("Hello")
```

---

## テーブル

情報整理にはテーブルを積極的に利用する。

---

## 図

ディレクトリ構成やシステム構成はテキスト図で記載する。

---

# 6. Naming Conventions

## Directory

小文字を使用する。

例

```text
requirements
design
adr
backend
frontend
tests
```

---

## Markdown Files

snake_caseを採用する。

例

```text
basic_design.md
database_design.md
api_design.md
project_conventions.md
```

---

## ADR

以下の命名規則を採用する。

```text
ADR-001-user-in-control.md

ADR-002-target-type-definition.md

ADR-003-category-definition.md
```

---

## Python

クラス

```text
IssueService

IssueRepository

IssueDTO
```

ファイル

```text
issue_service.py

issue_repository.py
```

---

# 7. Directory Structure

プロジェクト構成は以下を基本とする。

```text
cim/
├── backend/
├── frontend/
├── storage/
├── scripts/
├── tests/
├── docs/
├── README.md
├── LICENSE
└── .gitignore
```

各ディレクトリの責務を明確に分離する。

---

# 8. Git Workflow

GitHubを唯一のバージョン管理システムとする。

基本フロー

1. featureブランチ作成
2. 開発
3. コミット
4. Pull Request
5. レビュー
6. mainへマージ

mainブランチへ直接コミットしない。

---

# 9. Branch Naming

以下の命名規則を採用する。

```text
feature/issue-management

feature/ai-draft

feature/room-master

fix/login-error

docs/basic-design

refactor/issue-service
```

ブランチ名は目的が分かる名称とする。

---

# 10. Commit Message

コミットメッセージには Conventional Commits を採用する。

## 10.1 Format

```text
<type>: <summary>
```

例

```text
feat: add issue create API

fix: validate room number

docs: update basic design

refactor: simplify issue service

test: add issue service tests
```

## 10.2 Commit Types

| Type     | 説明       |
| -------- | -------- |
| feat     | 新機能      |
| fix      | バグ修正     |
| docs     | ドキュメント更新 |
| refactor | リファクタリング |
| test     | テスト追加・修正 |
| chore    | ビルド・設定変更 |

コミットメッセージは簡潔かつ内容が分かるものとする。

---

# 11. ADR Rules

ADR（Architecture Decision Record）は、プロジェクト全体へ影響する重要な設計判断を記録する。

## 11.1 ADR対象

以下はADRとして記録する。

* 設計原則
* ドメインモデル
* アーキテクチャ
* AI利用方針
* API設計方針
* データ管理方針
* セキュリティ方針

## 11.2 ADR対象外

以下は通常ADRとしない。

* 実装方法
* クラス構成
* メソッド名
* UIレイアウト調整
* 軽微なリファクタリング

## 11.3 ADR更新

AcceptedとなったADRは原則として内容を書き換えない。

設計変更を行う場合は、新しいADRを追加し、変更履歴を残す。

---

# 12. Design Rules

設計変更時は以下の順序で更新する。

1. 要件定義書
2. 基本設計書
3. 詳細設計書
4. ADR（必要な場合）
5. 実装

実装のみを先行して変更しない。

設計書と実装の整合性を常に維持する。

---

# 13. Coding Rules

## 13.1 Python

* PEP 8に従う。
* 型ヒントを使用する。
* Docstringを記述する。
* 可読性を優先する。

## 13.2 FastAPI

以下のレイヤー構成を採用する。

```text
Presentation Layer
        │
API Layer
        │
Service Layer
        │
Repository Layer
        │
Database
```

レイヤー間の責務を明確に分離する。

## 13.3 Repository Pattern

Repositoryはデータアクセスのみを担当する。

業務ロジックをRepositoryへ実装しない。

## 13.4 Service Layer

業務ロジックはService Layerへ実装する。

入力値検証（Validation）もService Layerで実施する。

---

# 14. AI Collaboration

AIは設計・実装を支援するツールとして利用する。

## 14.1 AIの役割

AIは以下を支援する。

* ドキュメント作成
* 設計レビュー
* コード生成
* テストコード生成
* リファクタリング提案

## 14.2 AI利用時の原則

* AIが生成した内容は必ずレビューする。
* AIが生成したコードを無条件に採用しない。
* 設計変更を伴う場合は、設計書またはADRを更新してから実装する。

---

# 15. Versioning Rules

## 15.1 Requirements

要件変更時は以下を更新する。

* Requirements
* CHANGELOG

## 15.2 Design

設計変更時は以下を更新する。

* Basic Design
* Detailed Design
* 必要に応じてADR

## 15.3 Implementation

実装のみの変更では設計書を更新しない。

ただし、設計との不整合が生じる場合は設計書を先に更新する。

---

# 16. Development Environment

標準開発環境を以下とする。

| 項目              | 内容                               |
| --------------- | -------------------------------- |
| OS              | Windows 11                       |
| Linux           | WSL2 Ubuntu LTS                  |
| Editor          | Visual Studio Code（Remote - WSL） |
| Backend         | FastAPI                          |
| Database        | SQLite                           |
| AI              | Ollama                           |
| Version Control | Git / GitHub                     |

## Deployment

初期版はWindows 11で運用する。

ただし、OS依存を避け、将来的にUbuntu Serverへ移行可能な設計とする。

---

# 17. Review Policy

レビューでは以下を確認する。

* 要件との整合性
* 設計原則との整合性
* 命名規則
* 可読性
* 保守性
* 拡張性

実装品質だけではなく、設計品質を重視する。

レビューで設計変更が必要と判断した場合は、実装より先に設計書を更新する。

---

# Revision History

| Version | Date       | Description     |
| ------- | ---------- | --------------- |
| 1.0     | 2026-06-30 | Initial version |
