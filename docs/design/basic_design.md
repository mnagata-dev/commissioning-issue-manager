# CIM Basic Design

**Document Version:** 1.1 **Status:** Review **Last Updated:** 2026-07-03 **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Synchronize with updated requirements and database design.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. System Overview
5. System Architecture
6. Design Principles
7. Domain Model
8. Functional Overview
9. Screen Overview
10. Screen Navigation
11. Use Cases
12. System Sequence
13. Data Flow
14. Authentication and Authorization
15. AI Integration
16. File Management
17. Error Handling
18. Logging
19. Directory Structure
20. External Interfaces
21. System Constraints
22. Future Enhancements

---

# 1. Purpose

本書は、CIM (Commissioning Issue Manager) の基本設計を定義することを目的とする。

要件定義書で定義した要求を実現するためのシステム構成、機能構成および主要な設計方針を定義する。

本書を基に、データベース設計、API設計、UI設計および詳細設計を実施する。

---

# 2. Scope

本書では以下を対象とする。

- システム全体構成
- アーキテクチャ
- ドメインモデル
- 機能構成
- 画面構成
- 認証・認可
- AI連携
- ファイル管理
- 外部インターフェース
- システム制約

以下は対象外とする。

- データベース詳細設計
- API詳細設計
- UI詳細設計
- クラス設計
- テスト設計

これらは各設計書で定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

|ドキュメント|説明|
|---|---|
|requirements.md|要件定義書|
|project_conventions.md|プロジェクト共通ルール|
|ADR-001 ～ ADR-005|アーキテクチャ設計判断|

---

# 4. System Overview

CIM は、 Lutron システムのコミッショニング業務において発生する Issue を管理するための Web アプリケーションである。

利用者は Project を選択し、 Issue の登録・更新・確認を行う。

AI (Ollama) は音声入力を解析し、 Issue Draft の作成を支援する。

AI は入力支援のみを担当し、業務データの最終決定は利用者が行う。

---

## 4.1 Development Environment

|項目|内容|
|---|---|
|OS|Windows 11|
|Linux|WSL2 Ubuntu LTS|
|IDE|Visual Studio Code|
|Backend|FastAPI|
|Database|SQLite|
|AI|Ollama|

---

## 4.2 Deployment Environment

初期版は Windows 11 へデプロイする。

アプリケーションは OS 依存を避け、将来的に Ubuntu Server へ移行可能な設計とする。

---

# 5. System Architecture

本システムはレイヤードアーキテクチャを採用する。

``` text
+------------------------------------------------------+
|                    Web Browser                       |
|             (PC / Smartphone Browser)                |
+---------------------------+--------------------------+
                            |
                            v
+------------------------------------------------------+
|                    FastAPI Backend                   |
+------------------------------------------------------+
| Presentation Layer                                   |
+------------------------------------------------------+
| Service Layer                                        |
+------------------------------------------------------+
| Repository Layer                                     |
+------------------------------------------------------+
                            |
            +---------------+---------------+
            |                               |
            v                               v
+-------------------------+       +----------------------+
|        SQLite           |       |       Ollama         |
|  (Business Data)        |       | (AI Draft Support)   |
+-------------------------+       +----------------------+
            |
            v
+-------------------------+
|     Local Storage       |
| (Attachment Files)      |
+-------------------------+
```

---

## 5.1 Layer Responsibilities

|レイヤー|責務|
|---|---|
|Presentation Layer|画面表示、入力受付、API呼び出し|
|Service Layer|業務ロジック、入力値検証|
|Repository Layer|データアクセス|
|SQLite|業務データの永続化|
|Local Storage|添付ファイル保存|
|Ollama|AI Draft生成|

---

# 6. Design Principles

本システムでは以下の設計原則を採用する。

|設計原則|内容|
|---|---|
|User in Control|最終判断は常に利用者が行う。|
|Business First|コミッショニング業務を最優先に設計する。|
|Documentation First|設計を先に定義してから実装する。|
|Layered Architecture|レイヤーごとに責務を分離する。|
|Single Responsibility Principle|1つのクラス・モジュールは1つの責務のみを持つ。|
|Repository Pattern|データアクセスをRepositoryへ集約する。|
|Service Layer Pattern|業務ロジックをService Layerへ集約する。|
|API First|APIを中心にシステムを設計する。|
|Master Data First|マスタデータを基準に業務データを管理する。|

---

## 6.1 Design Policies

システム設計では以下の方針を採用する。

- シンプルで保守しやすい構成とする。
- 業務ロジックとデータアクセスを分離する。
- AI は入力支援のみを担当する。
- OS 依存を避ける。
- 将来的な機能追加を考慮した拡張性を確保する。

---

# 7. Domain Model

本章では、本システムで扱う主要なドメインモデルを定義する。

## 7.1 Domain Model Overview

``` text
Hotel
├── RoomType
│   └── Room
└── Project
    └── Issue
        ├── Comment
        └── Attachment

User
```

---

## 7.2 Domain Models

|モデル|説明|
|---|---|
|Hotel|Project、RoomType、Room を管理する施設・建物|
|Project|コミッショニング対象となる案件|
|User|システム利用者 (username 、 password_hash 、 display_name 、 role を持つ)|
|RoomType|部屋種別|
|Room|Hotel 内の部屋|
|Issue|Project に属し、必要に応じて Room を参照する課題・確認事項|
|Comment|Issue に対するコメント履歴|
|Attachment|Issue へ添付する写真・動画などのファイル|

---

## 7.3 Domain Relationships

|Parent|Cardinality|Child|
|---|---|---|
|Hotel|1 : N|Room|
|Hotel|1 : N|RoomType|
|Hotel|1 : N|Project|
|RoomType|1 : N|Room|
|Project|1 : N|Issue|
|Issue|---|Room を任意で参照する。|
|Issue|1 : N|Comment|
|Issue|1 : N|Attachment|

---

# 8. Functional Overview

本システムは以下の機能群で構成される。

## Functional Structure

``` text
CIM
├── Authentication
├── Project Selection
├── Issue Management
├── AI Draft
├── Comment Management
├── Attachment Management
└── Administration
    ├── Project Management
    ├── User Management
    └── Master Data Management
```

---

## Functional List

|機能|説明|
|---|---|
|Authentication|利用者認証|
|Project Selection|作業対象Projectの選択|
|Issue Management|Issueの登録・更新・参照|
|AI Draft|音声入力からIssue Draftを生成|
|Comment Management|Commentの追加・参照|
|Attachment Management|写真・動画の添付・削除|
|Administration|管理者向け管理機能|

---

## 8.1 Authentication

認証済み利用者のみシステムを利用できる。

---

## 8.2 Project Selection

Engineerは作業対象となるProjectを選択する。

選択したProjectを基準として業務を行う。

---

## 8.3 Issue Management

Issue管理は本システムの中心機能である。

利用者はIssueの登録、更新、参照およびStatus変更を行う。

---

## 8.4 AI Draft

AIは音声入力を解析し、Issue Draftを生成する。

AIは業務データを保存せず、利用者が内容を確認・修正した後にIssue登録を行う。

---

## 8.5 Comment Management

Issueに対するCommentを管理する。

Commentは履歴として保持する。

---

## 8.6 Attachment Management

Issueに対して写真・動画などのAttachmentを管理する。

添付ファイル本体はLocal Storageに保存する。

---

## 8.7 Administration

Administratorのみ利用できる管理機能を提供する。

Administrationは以下の機能で構成される。

- Project Management
- User Management
- Master Data Management

---

# 9. Screen Overview

本システムで提供する主要画面を以下に示す。

|画面|説明|
|---|---|
|Login|ログイン画面|
|Project Selection|Project選択画面|
|Issue List|Issue一覧画面|
|Issue Detail|Issue詳細画面|
|Issue Create|Issue登録画面|
|Issue Edit|Issue編集画面|
|Administration|管理メニュー画面|

---

# 10. Screen Navigation

画面遷移を以下に示す。

``` text
Login
  │
  ▼
Project Selection
  │
  ▼
Issue List
  ├──────────────┐
  ▼              ▼
Issue Detail   Issue Create
  │              │
  ▼              ▼
Issue Edit ──────┘

Administrator
      │
      ▼
Administration
 ├── Project Management
 ├── User Management
 └── Master Data Management
```

---

# 11. Use Cases

主要なユースケースを以下に示す。

|利用者|ユースケース|
|---|---|
|Engineer|Projectを選択する。|
|Engineer|Issueを登録する。|
|Engineer|Issueを更新する。|
|Engineer|IssueのStatusを変更する。|
|Engineer|Commentを追加する。|
|Engineer|Attachmentを追加する。|
|Engineer|AI Draftを利用する。|
|Administrator|Projectを管理する。|
|Administrator|Userを管理する。|
|Administrator|Master Dataを管理する。|

---

# 12. System Sequence

本章では、主要な業務フローにおけるシステム全体の処理シーケンスを示す。

詳細なAPI処理およびクラス間のシーケンスは、詳細設計書で定義する。

---

## 12.1 Issue Registration

Issue登録時のシステム処理を以下に示す。

``` text
Engineer
    │
    │ Issue入力
    ▼
Frontend
    │
    │ POST /api/issues
    ▼
FastAPI
    │
    ▼
IssueService
    │
    ▼
IssueRepository
    │
    ▼
SQLite
    │
    ▼
Response
    │
    ▼
Frontend
    │
    ▼
Engineer
```

Issue登録時には、Service Layerで入力値の検証を行う。

---

## 12.2 AI Draft Generation

AI Draft生成時のシステム処理を以下に示す。

``` text
Engineer
    │
    │ 音声入力
    ▼
Frontend
    │
    ▼
FastAPI
    │
    ▼
AI Service
    │
    ▼
Ollama
    │
    ▼
AI Draft
    │
    ▼
Frontend
    │
    ▼
Engineer
```

AIはIssueを保存しない。

生成されたAI Draftは利用者が確認・修正した後にIssue登録へ利用する。

---

## 12.3 Attachment Upload

Attachment追加時のシステム処理を以下に示す。

``` text
Engineer
    │
    ▼
Frontend
    │
    ▼
FastAPI
    │
    ▼
AttachmentService
    │
    ├──────────────┐
    ▼              ▼
AttachmentRepository  Local Storage
    │
    ▼
SQLite
    │
    ▼
Response
```

添付ファイル本体はLocal Storageへ保存する。

ファイル情報はSQLiteで管理する。

---

# 13. Data Flow

本章では、システム内におけるデータの流れを示す。

## 13.1 Issue Registration

``` text
Engineer
      │
      ▼
Frontend
      │
      ▼
FastAPI
      │
      ▼
Service Layer
      │
      ▼
Repository Layer
      │
      ▼
SQLite
```

---

## 13.2 AI Draft

``` text
Engineer
      │
      ▼
Frontend
      │
      ▼
FastAPI
      │
      ▼
AI Service
      │
      ▼
Ollama
      │
      ▼
AI Draft
      │
      ▼
Engineer
```

---

## 13.3 Attachment Upload

``` text
Engineer
      │
      ▼
Frontend
      │
      ▼
FastAPI
      │
      ├──────────────┐
      ▼              ▼
SQLite        Local Storage
```

---

# 14. Authentication and Authorization

本システムでは認証（Authentication）と認可（Authorization）を分離して管理する。

---

## 14.1 Authentication

利用者は username と password により認証後、システムを利用する。

username はログイン ID として利用し、メールアドレス形式も許容する。

認証方式の詳細は API 設計書および詳細設計書で定義する。

---

## 14.2 Authorization

認可は利用者のRoleに基づいて行う。

|Role|権限|
|---|---|
|Administrator|すべての機能を利用できる。|
|Engineer|コミッショニング業務に必要な機能を利用できる。|

---

## 14.3 Administration

Administration機能はAdministratorのみ利用できる。

以下の管理機能を提供する。

- Project Management
- User Management
- Master Data Management

---

# 15. AI Integration

本システムではローカルLLM（Ollama）を利用する。

AIは入力支援のみを担当し、業務上の最終判断は利用者が行う。

---

## 15.1 AI Responsibilities

AIは以下を実施する。

- 音声入力の解析
- TargetTypeの推定
- Targetの推定
- Categoryの推定
- Descriptionの生成

---

## 15.2 AI Limitations

AIは以下を実施しない。

- Issue保存
- Issue更新
- Status変更
- Comment追加
- Attachment追加
- Master Data更新

---

## 15.3 User Confirmation

AIが生成した内容は、利用者が確認・修正した後にIssue登録を行う。

---

# 16. File Management

本章では、添付ファイルの管理方針を定義する。

---

## 16.1 Supported File Types

初期版では以下を対象とする。

- Image
- Video

---

## 16.2 Storage Policy

添付ファイル本体はLocal Storageへ保存する。

ファイル管理情報はSQLiteで管理する。

---

## 16.3 File Lifecycle

Attachmentは以下のライフサイクルを持つ。

1.  アップロード
2.  Issueへ関連付け
3.  参照
4.  削除

初期版ではAttachmentの編集機能は提供しない。

---

# 17. Error Handling

本章では、本システムのエラーハンドリング方針を定義する。

---

## 17.1 Error Classification

システムで扱うエラーを以下に分類する。

|種類|説明|
|---|---|
|Validation Error|入力値の検証エラー|
|Authentication Error|認証エラー|
|Authorization Error|認可エラー|
|Business Error|業務ルール違反|
|System Error|システム内部エラー|
|External Service Error|外部サービス（Ollama等）との連携エラー|

---

## 17.2 Error Handling Policy

- 利用者に理解しやすいエラーメッセージを表示する。
- システム内部の詳細情報は利用者へ表示しない。
- システム内部エラーはログへ記録する。
- エラー発生時もデータ整合性を維持する。

---

# 18. Logging

本章では、ログ管理方針を定義する。

---

## 18.1 Logging Policy

システムの運用および障害解析のため、必要なログを記録する。

---

## 18.2 Log Categories

|ログ種別|内容|
|---|---|
|Application Log|アプリケーションの動作ログ|
|Error Log|エラー情報|
|AI Log|AI処理の実行状況|
|Audit Log|将来対応予定|

---

## 18.3 Log Retention

ログの保存期間および運用方法は、運用環境に応じて定義する。

詳細は運用設計書で定義する。

---

# 19. Directory Structure

本システムのディレクトリ構成を以下に示す。

``` text
cim/
├── backend/
├── frontend/
├── storage/
│   ├── attachments/
│   └── database/
├── docs/
├── scripts/
├── tests/
├── README.md
├── LICENSE
└── .gitignore
```

---

## 19.1 Directory Responsibilities

|ディレクトリ|役割|
|---|---|
|backend|バックエンドアプリケーション|
|frontend|フロントエンドアプリケーション|
|storage|SQLiteデータベースおよび添付ファイル|
|docs|設計書・ドキュメント|
|scripts|補助スクリプト|
|tests|テストコード|

---

# 20. External Interfaces

本システムが利用する外部インターフェースを以下に示す。

|インターフェース|用途|
|---|---|
|Ollama API|AI Draft生成|
|File System|添付ファイル保存|
|SQLite|業務データ保存|

---

## 20.1 AI Interface

AI連携はOllamaとのAPI通信によって実現する。

通信方式およびリクエスト・レスポンス仕様はAPI設計書で定義する。

---

## 20.2 File Interface

添付ファイルはローカルファイルシステムへ保存する。

ファイル管理情報はSQLiteで管理する。

---

# 21. System Constraints

初期版におけるシステム制約を以下に示す。

|項目|内容|
|---|---|
|Database|SQLiteを利用する。|
|File Storage|Local Storageを利用する。|
|AI|Ollamaを利用する。|
|Deployment|Windows 11環境へデプロイする。|
|Master Data Management|CLIまたはCSVによる管理とする。|
|Issue Deletion|提供しない。|
|Comment Edit/Delete|提供しない。|
|Attachment Edit|提供しない。|

---

# 22. Future Enhancements

将来的な拡張を以下に示す。

- Viewerロールの追加
- Managerロールの追加
- Customerロールの追加
- Web画面によるProject管理
- Web画面によるUser管理
- Web画面によるMaster Data管理
- Docker対応
- Ubuntu Serverへのデプロイ
- クラウド環境への展開
- AI機能の高度化

これらは初期版の設計範囲には含めない。

---

# End of Document
