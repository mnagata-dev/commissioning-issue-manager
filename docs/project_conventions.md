# CIM Project Conventions

- **Document Version:** 1.1
- **Status:** Draft
- **Last Updated:** 2026-07-08
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-08|Strengthen documentation principles and document hierarchy. Clarify document responsibilities, consistency rules, terminology, and document maintenance policies.|

---

# Table of Contents

1. Purpose
2. Project Principles
3. Design Documentation Principles
4. Documentation Rules
5. Language Policy
6. Markdown Rules
7. Naming Conventions
8. Directory Structure
9. Git Workflow
10. Branch Naming
11. Commit Message
12. ADR Rules
13. Design Rules
14. Coding Rules
15. AI Collaboration
16. Versioning Rules
17. Development Environment
18. Review Policy

---

# 1. Purpose

本ドキュメントは、CIM (Commissioning Issue Manager) プロジェクトにおける共通ルールを定義することを目的とする。

本ドキュメントは、要件定義、設計、実装、テストおよび運用において、一貫した品質を維持するための基準を提供する。

本プロジェクトへ新たなドキュメントまたはソースコードを追加する場合は、本ドキュメントのルールに従う。

---

# 2. Project Principles

本プロジェクトでは、以下の設計原則を採用する。

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

新しい設計判断を行う場合は、これらの設計原則との整合性を確認する。

---

# 3. Design Documentation Principles

本章では、本プロジェクトにおける設計ドキュメントの作成原則を定義する。

これらの原則は、Requirements、Design Documents、ADR および README を含むすべての設計ドキュメントに適用する。

---

## 3.1 Single Source of Truth

同一の内容は、一つのドキュメントのみを正式な定義元 (Single Source of Truth) とする。

他のドキュメントでは内容を重複して定義せず、必要に応じて参照する。

ドキュメント間で同一内容を複数箇所に記載しない。

---

## 3.2 Definition Before Usage

用語、概念およびドメインモデルは、使用する前に定義する。

特に以下については、最初に定義してから本文中で使用する。

- Domain Model
- Target Type
- Category
- Status
- Role

---

## 3.3 Normative Before Informative

要求事項および仕様を先に記載する。

背景、理由、補足説明および例は、その後に記載する。

要求と説明を混在させない。

---

## 3.4 One Responsibility per Document

各ドキュメントは明確な責務を持つ。

|Document|Responsibility|
|---|---|
|Requirements|何を作るか (What)|
|ADR|なぜその設計を採用したか (Why)|
|Design Documents|どのように実現するか (How)|
|Source Code|実際の実装|

責務を超える内容は記載しない。

---

## 3.5 Documentation Hierarchy

ドキュメントは以下の階層構造を持つ。

```text
Requirements
      │
      ▼
Basic Design
      │
      ▼
Database Design
API Design
UI Design
Detailed Design
Test Design
      │
      ▼
Implementation
```

上位ドキュメントと下位ドキュメントで内容が矛盾する場合は、上位ドキュメントを優先する。

優先順位は以下とする。

1. Requirements
2. Basic Design
3. Database Design / API Design / UI Design / Detailed Design / Test Design
4. Implementation

---

## 3.6 Cross References Instead of Duplication

共通内容は複数のドキュメントへコピーしない。

必要な場合は、正式な定義元を参照する。

内容の重複は保守コストおよび不整合の原因となるため避ける。

---

## 3.7 Design Consistency

ドキュメントを修正する場合は、関連するドキュメントとの整合性を確認する。

変更内容が他のドキュメントへ影響する場合は、同一の変更で関連ドキュメントも更新する。

ドキュメント間の整合性は、個々のドキュメントの完成度よりも優先する。

---

# 4. Documentation Rules

## 4.1 Documentation Structure

ドキュメントは以下の構成とする。

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

## 4.2 Document Roles

各ドキュメントの役割を以下に示す。

|Document|Role|
|---|---|
|README|プロジェクト全体の入口|
|Project Conventions|プロジェクト共通ルール|
|Requirements|要件定義|
|Design|設計|
|ADR|設計判断の記録|
|Images|図および画像|

各ドキュメントは自身の責務のみを定義する。

---

## 4.3 Documentation Policy

ドキュメントは実装より先に作成・更新する。

設計変更を伴う場合は、設計書を更新してから実装を行う。

ドキュメントは Git によりバージョン管理する。

Markdown 形式を採用する。

---

## 4.4 Documentation Workflow

ドキュメントは以下の順序で作成および更新する。

1. Requirements
2. Basic Design
3. Database Design
4. API Design
5. UI Design
6. Detailed Design
7. Test Design
8. ADR (必要な場合)
9. Implementation

上位ドキュメントが完成してから下位ドキュメントを更新する。

---

## 4.5 Design Review Policy

レビューでは以下を確認する。

- Requirements との整合性
- 上位ドキュメントとの整合性
- 下位ドキュメントへの影響
- 用語の統一
- 表記ゆれ
- Markdown ルール
- ドメインモデルとの整合性

---

## 4.6 Specification Changes and Editorial Changes

ドキュメントの変更は以下の二種類に分類する。

### Specification Change

要件または設計を変更する修正。

例

- 新機能追加
- ドメインモデル変更
- API仕様変更
- データモデル変更

必要に応じて Requirements、CHANGELOG および ADR を更新する。

---

### Editorial Change

仕様を変更しない修正。

例

- 誤字脱字
- 表記ゆれ
- 用語統一
- Markdown 修正
- 可読性向上

Editorial Change は仕様変更として扱わない。

---

# 5. Language Policy

## 5.1 Basic Policy

本文は日本語で記述する。

コード、API、クラス名およびドメインモデルは英語表記を採用する。

---

## 5.2 Domain Model

以下は英語表記とする。

- User
- Hotel
- Project
- RoomType
- Room
- Issue
- Comment
- Attachment

本文中では必要に応じて日本語を併記してよい。

例

```text
Room (客室)
```

---

## 5.3 User Terminology

本文では「ユーザー」を使用する。

データモデルおよびクラス名は User を使用する。

ロール名は以下を使用する。

- Administrator
- Engineer

---

## 5.4 Feature Names

以下は英語表記を採用する。

- Authentication
- Project Management
- Issue Management
- AI Draft
- Comment Management
- Attachment Management

---

## 5.5 Source Code

ソースコード中の識別子は英語で記述する。

対象は以下を含む。

- クラス名
- 関数名
- メソッド名
- 変数名
- 定数名
- ファイル名
- ディレクトリ名
- API エンドポイント
- JSON キー
- テーブル名
- カラム名

日本語のローマ字表記は使用しない。

例

|Good|Bad|
|---|---|
|room_id|heya_id|
|lighting|shoumei|
|issue_service.py|mondai_service.py|
|created_at|sakusei_bi|

コードコメントおよび docstring は原則として英語で記述する。

設計意図や業務知識など、日本語の方が理解しやすい場合は日本語コメントを認める。

ユーザー向け表示文言は UI 設計に従う。

---

## 5.6 Tables

表の見出しは日本語を基本とする。

例

|機能|説明|
|---|---|
|Authentication|ユーザー認証|

---

# 6. Markdown Rules

## 6.1 Headings

以下の見出しレベルを使用する。

```text
#
##
###
```

---

## 6.2 Horizontal Rule

Horizontal Rule は

```text
---
```

を使用する。

前後には空行を入れる。

---

## 6.3 Lists

箇条書きはハイフン (-) を使用する。

アスタリスク (*) は使用しない。

---

## 6.4 Tables

テーブルは以下の形式を使用する。

```text
|Header|Header|
|---|---|
|Value|Value|
```

情報整理には積極的にテーブルを利用する。

---

## 6.5 Code Blocks

コードはコードブロックを使用する。

可能な限り言語指定を行う。

例

```python
def hello():
    print("Hello")
```

---

## 6.6 Diagrams

システム構成およびディレクトリ構成は、可能な限りテキスト図で表現する。

画像を使用する場合は images ディレクトリで管理する。

---

## 6.7 Terminology

同一ドキュメント内では用語を統一する。

例

- 「Issue を登録する」と「Issue を作成する」を混在させない。
- 「Target Type」と「TargetType」を混在させない。
- 「ユーザー」と「利用者」を混在させない。

---

# 7. Naming Conventions

## 7.1 Directory

ディレクトリ名は小文字を使用する。

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

## 7.2 Markdown Files

Markdown ファイル名は snake_case を採用する。

例

```text
basic_design.md
database_design.md
api_design.md
project_conventions.md
```

---

## 7.3 ADR

ADR は以下の命名規則を採用する。

```text
ADR-001-user-in-control.md

ADR-002-target-type-definition.md

ADR-003-category-definition.md
```

---

## 7.4 Python

クラス名は PascalCase を採用する。

例

```text
IssueService

IssueRepository

IssueDTO
```

ファイル名は snake_case を採用する。

例

```text
issue_service.py

issue_repository.py
```

---

## 7.5 Database

テーブル名およびカラム名は snake_case を採用する。

例

```text
users
room_types
created_at
updated_at
password_hash
```

---

## 7.6 REST API

REST API は複数形リソース名を使用する。

例

```text
/api/projects

/api/issues

/api/issues/{issue_id}

/api/issues/{issue_id}/comments
```

HTTP メソッドは REST の一般的な設計方針に従う。

---

# 8. Directory Structure

## 8.1 Project Structure

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

## 8.2 Documentation Structure

設計ドキュメントは以下の構成とする。

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

## 8.3 Backend Structure

Backend は責務ごとにディレクトリを分離する。

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── alembic/
├── tests/
└── pyproject.toml
```

レイヤー間の責務を明確に分離する。

---

# 9. Git Workflow

GitHub を唯一のバージョン管理システムとする。

基本フローは以下とする。

1. ブランチ作成
2. ドキュメント更新
3. レビュー
4. 実装
5. Commit
6. Push
7. Pull Request
8. Review
9. Merge

main ブランチへ直接 Commit を行わない。

設計変更を含む場合は、設計書を更新してから実装する。

---

# 10. Branch Naming

以下の命名規則を採用する。

```text
feature/issue-management

feature/ai-draft

feature/room-master

fix/login-error

docs/basic-design

docs/update-design-after-review

refactor/issue-service
```

ブランチ名は目的が分かる名称とする。

---

# 11. Commit Message

## 11.1 Convention

コミットメッセージは Conventional Commits に従う。

---

## 11.2 Prefix

以下のプレフィックスを使用する。

- feat
- fix
- docs
- refactor
- test
- chore

---

## 11.3 Rules

コミットメッセージは英語で記述する。

命令形 (Imperative Mood) を使用する。

1つのコミットでは1つの目的に限定する。

ドキュメント更新のみの場合は docs を使用する。

---

## 11.4 Examples

```text
feat: add issue API

fix: validate room type

docs: update requirements

docs: update project conventions

refactor: simplify repository layer

test: add issue service tests

chore: update dependencies
```

---

# 12. ADR Rules

ADR (Architecture Decision Record) は、プロジェクト全体へ影響する重要な設計判断を記録する。

---

## 12.1 ADR Target

以下は ADR として記録する。

- 設計原則
- ドメインモデル
- アーキテクチャ
- AI 利用方針
- API 設計方針
- データ管理方針
- セキュリティ方針

---

## 12.2 Not Target

以下は通常 ADR の対象としない。

- 実装方法
- クラス構成
- メソッド名
- UI レイアウト調整
- 軽微なリファクタリング
- Editorial Change

---

## 12.3 ADR Lifecycle

ADR は以下の状態を持つ。

|Status|Description|
|---|---|
|Proposed|提案中|
|Accepted|採用済み|
|Superseded|新しい ADR に置き換えられた|
|Deprecated|非推奨|

Accepted となった ADR は原則として書き換えない。

設計変更を行う場合は、新しい ADR を追加し、変更履歴を残す。

---

## 12.4 Relationship with Requirements

ADR は Requirements を変更するためのドキュメントではない。

Requirements を実現するための設計判断および採用理由を記録する。

Requirements と矛盾する ADR は作成しない。

---

# 13. Design Rules

## 13.1 Design Workflow

設計変更時は以下の順序で更新する。

1. Requirements
2. Basic Design
3. Database Design
4. API Design
5. UI Design
6. Detailed Design
7. Test Design
8. ADR (必要な場合)
9. Implementation

実装のみを先行して変更しない。

---

## 13.2 Document Consistency

設計変更を行う場合は、関連する設計書との整合性を確認する。

必要に応じて複数のドキュメントを同一変更で更新する。

---

## 13.3 Business First

業務要件を最優先とする。

データベース構造や実装上の都合によって要件を決定しない。

---

## 13.4 Simplicity First

初期版では必要最小限の設計を採用する。

将来必要となる可能性だけを理由に機能を追加しない。

---

## 13.5 User in Control

AI は入力支援のみを担当する。

業務上の最終判断は必ずユーザーが行う。

AI が業務データを自動的に登録・更新する設計は採用しない。

---

## 13.6 Design Review

設計レビューでは以下を確認する。

- Requirements との整合性
- ドメインモデル
- AI の責務
- User in Control
- Simplicity First
- ドキュメント間整合性
- ADR との整合性

---

# 14. Coding Rules

## 14.1 Python

以下を基本方針とする。

- PEP 8 に従う。
- 型ヒントを使用する。
- Docstring を記述する。
- 可読性を優先する。

---

## 14.2 FastAPI

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

各レイヤーの責務を明確に分離する。

---

## 14.3 Repository Pattern

Repository はデータアクセスのみを担当する。

業務ロジックを Repository に実装しない。

---

## 14.4 Service Layer

業務ロジックは Service Layer へ実装する。

Validation も Service Layer で実施する。

---

## 14.5 Source Code Consistency

ソースコードは設計書との整合性を維持する。

設計変更が必要な場合は、設計書を先に更新する。

---

# 15. AI Collaboration

AI は設計および実装を支援するツールとして利用する。

---

## 15.1 AI Responsibilities

AI は以下を支援する。

- ドキュメント作成
- 設計レビュー
- コード生成
- テストコード生成
- リファクタリング提案

---

## 15.2 AI Review Policy

AI が生成した内容は必ず人がレビューする。

AI が生成した内容を無条件に採用しない。

---

## 15.3 Design First

設計変更を伴う場合は、設計書または ADR を更新してから実装する。

---

## 15.4 AI Limitations

AI は設計支援ツールであり、プロジェクトの意思決定者ではない。

最終的な設計判断および実装判断はプロジェクトメンバーが行う。

---

# 16. Versioning Rules

## 16.1 Requirements

要件変更時は以下を更新する。

- Requirements
- CHANGELOG

必要に応じて関連する ADR および設計書も更新する。

---

## 16.2 Design

設計変更時は以下を更新する。

- Basic Design
- Database Design
- API Design
- UI Design
- Detailed Design
- Test Design

必要に応じて ADR を追加または更新する。

---

## 16.3 Editorial Change

仕様を変更しない修正では Requirements のバージョンを変更しない。

例

- 誤字脱字
- 表記ゆれ
- Markdown 修正
- 可読性向上

必要に応じて CHANGELOG に編集内容を記録する。

---

## 16.4 Implementation

実装のみを変更する場合は設計書を更新しない。

ただし、設計との不整合が生じる場合は、実装より先に設計書を更新する。

---

# 17. Development Environment

## 17.1 Standard Development Environment

標準開発環境を以下とする。

|Item|Description|
|---|---|
|OS|Windows 11|
|Linux|WSL2 Ubuntu LTS|
|Editor|Visual Studio Code (Remote - WSL)|
|Backend|FastAPI|
|Database|SQLite|
|AI|Ollama|
|Version Control|Git / GitHub|

---

## 17.2 Deployment Environment

初期版は Windows 11 上で運用する。

OS 依存を避け、将来的に Ubuntu Server へ移行可能な設計とする。

---

## 17.3 Development Policy

ローカル環境を基本とし、インターネット接続が利用できない現場でも開発および動作確認が可能な構成を目指す。

---

# 18. Review Policy

レビューでは実装品質だけではなく、設計品質を重視する。

---

## 18.1 Review Items

以下を確認する。

- Requirements との整合性
- Project Principles との整合性
- Design Documentation Principles との整合性
- ドキュメント間整合性
- ドメインモデル
- AI の責務
- User in Control
- 命名規則
- 用語統一
- Markdown Rules
- 可読性
- 保守性
- 拡張性

---

## 18.2 Review Order

レビューは上位ドキュメントから順番に実施する。

1. Requirements
2. Basic Design
3. Database Design
4. API Design
5. UI Design
6. Detailed Design
7. Test Design
8. ADR
9. Implementation

---

## 18.3 Review Result

レビュー結果は以下に分類する。

|Category|Description|
|---|---|
|Critical|Requirements または設計思想との矛盾|
|Major|将来の保守性または設計品質へ大きく影響する問題|
|Minor|可読性、保守性または理解しやすさの改善|
|Editorial|仕様変更を伴わない編集改善|

---

## 18.4 Review Responsibility

レビュー担当者は独断で仕様を変更しない。

仕様変更が必要と判断した場合は、Requirements を起点として変更を提案する。

下位ドキュメントのみを修正して、Requirements との不整合を解消しない。

レビューでは、Requirements を最上位ドキュメントとして扱う。

---

## 18.5 Review Principle

レビューでは必要最小限の変更を行う。

不要なリファクタリングは行わない。

プロジェクト全体の整合性を最優先とする。

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-08|Strengthen documentation principles, documentation workflow, review policy and document hierarchy.|

---

# End of Document
