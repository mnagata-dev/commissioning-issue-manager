# CIM Detailed Design

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-09
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Synchronize with updated basic design and database design.|
|1.2|2026-07-09|Align with Requirements v1.2, Database Design, API Design, and UI Design. Simplify Target Type, update AI Draft design, validation rules, and related service definitions.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. Application Architecture
5. Backend Directory Structure
6. Layer Responsibilities
7. Domain Models
8. DTO Design
9. Service Design
10. Repository Design
11. Validation Design
12. Error Handling Design
13. Authentication and Authorization Design
14. AI Service Design
15. File Storage Design
16. Future Enhancements

---

# 1. Purpose

本書は、CIM (Commissioning Issue Manager) の詳細設計を定義することを目的とする。

本書では、実装に必要となるバックエンド構成、レイヤー責務、DTO、Service、Repository、Validation、Error Handling、AI 連携、File Storage の設計を定義する。

本書を基に、FastAPI アプリケーションの実装を行う。

---

# 2. Scope

本書では以下を対象とする。

- Backend アプリケーション構成
- ディレクトリ構成
- Layer 責務
- Domain Model
- DTO
- Service
- Repository
- Validation
- Error Handling
- Authentication / Authorization
- AI Service
- File Storage

以下は対象外とする。

- 要件定義
- 基本設計
- DB テーブル定義
- API 仕様
- UI 設計
- テストケース

これらは各設計書で定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

|ドキュメント|説明|
|---|---|
|requirements.md|要件定義書|
|basic_design.md|基本設計書|
|database_design.md|データベース設計書|
|api_design.md|API 設計書|
|ui_design.md|UI 設計書|
|project_conventions.md|プロジェクト共通ルール|
|ADR-001|User in Control|
|ADR-002|TargetType Definition|
|ADR-003|Category Definition|
|ADR-004|Room Model Design|
|ADR-005|Issue as Aggregate Root|

---

# 4. Application Architecture

本システムは FastAPI を利用したレイヤードアーキテクチャを採用する。

```text
Frontend
   │
   ▼
API Router
   │
   ▼
Service
   │
   ▼
Repository
   │
   ▼
Database
```

AI 連携および File Storage は Service Layer から利用する。

```text
Service
 ├── Repository
 ├── AI Client
 └── Storage Service
```

---

# 5. Backend Directory Structure

Backend のディレクトリ構成を以下に示す。

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── projects.py
│   │       ├── issues.py
│   │       ├── ai.py
│   │       ├── comments.py
│   │       └── attachments.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── hotel.py
│   │   ├── project.py
│   │   ├── room_type.py
│   │   ├── room.py
│   │   ├── issue.py
│   │   ├── comment.py
│   │   └── attachment.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── project.py
│   │   ├── issue.py
│   │   ├── ai.py
│   │   ├── comment.py
│   │   └── attachment.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   ├── issue_service.py
│   │   ├── ai_service.py
│   │   ├── comment_service.py
│   │   ├── attachment_service.py
│   │   └── storage_service.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── project_repository.py
│   │   ├── room_repository.py
│   │   ├── issue_repository.py
│   │   ├── comment_repository.py
│   │   └── attachment_repository.py
│   │
│   └── db/
│       ├── session.py
│       └── base.py
│
├── tests/
├── requirements.txt
└── README.md
```

---

# 6. Layer Responsibilities

## 6.1 API Router

API Router は HTTP リクエストを受け取り、Service を呼び出す。

API Router は業務ロジックを持たない。

主な責務は以下とする。

- Request 受信
- Request DTO の受け取り
- 認証済み User の取得
- Service 呼び出し
- Response DTO の返却

---

## 6.2 Service Layer

Service Layer は業務ロジックを担当する。

主な責務は以下とする。

- 業務ルールの検証
- Repository 呼び出し
- AI Service 呼び出し
- Storage Service 呼び出し
- トランザクション単位の制御
- Domain Model と DTO の変換補助

初期版では、1 API リクエストを 1 トランザクションとして処理する。

---

## 6.3 Repository Layer

Repository Layer はデータアクセスを担当する。

Repository は業務ロジックを持たない。

主な責務は以下とする。

- データ取得
- データ登録
- データ更新
- データ削除
- 検索条件に基づく Query 実行

---

## 6.4 Models

Models は DB テーブルに対応する SQLAlchemy モデルを定義する。

---

## 6.5 Schemas

Schemas は Pydantic を利用した DTO を定義する。

主な用途は以下とする。

- Request DTO
- Response DTO
- Internal DTO

---

## 6.6 Core

Core にはアプリケーション全体で利用する共通機能を配置する。

例：

- 設定
- Security
- 共通例外
- 共通エラー定義

---

# 7. Domain Models

本章では、システムで利用するドメインモデルを定義する。

ドメインモデルは業務上の概念を表現し、SQLAlchemy Model とは役割を分離する。

初期版では、Repository が SQLAlchemy Model を扱い、Service Layer がドメインルールを適用する。

---

## 7.1 Domain Model Overview

本システムで扱う主要なドメインモデルを以下に示す。

|Domain Model|説明|
|---|---|
|User|システムユーザー (username、password_hash、display_name、role)|
|Hotel|ホテル・施設|
|Project|コミッショニング案件|
|RoomType|部屋種別|
|Room|Hotel に属する部屋|
|Issue|Project に属し、必要に応じて Room を参照する課題|
|Comment|Issue へのコメント|
|Attachment|Issue への添付ファイル|

---

## 7.2 Aggregate

本システムでは Issue を Aggregate Root とする。

```text
Issue
 ├── Comment
 └── Attachment
```

Comment および Attachment は必ず Issue に属する。

単独では生成・管理しない。

---

## 7.3 Domain Responsibilities

|Domain|主な責務|
|---|---|
|User|システムユーザー|
|Hotel|コミッショニング対象施設|
|Project|コミッショニング案件|
|RoomType|客室種別|
|Room|Hotel 内の客室|
|Issue|コミッショニング時に発生した課題|
|Comment|Issue のコメント|
|Attachment|Issue の添付ファイル|

---

# 8. DTO Design

本章では、API で利用する DTO (Data Transfer Object) を定義する。

DTO は Pydantic Model として実装する。

---

## 8.1 Authentication DTO

### LoginRequest

```python
username: str
password: str
```

---

### CurrentUserResponse

```python
id: int
username: str
display_name: str
role: str
```

---

## 8.2 Project DTO

### ProjectResponse

```python
id: int
name: str
hotel: dict
```

---

### ProjectListResponse

```python
projects: list[ProjectResponse]
```

---

## 8.3 Issue DTO

### CreateIssueRequest

```python
room_id: int | None
target_type: str
target: str | None
category: str
description: str
```

---

### UpdateIssueRequest

```python
room_id: int | None
target_type: str
target: str | None
category: str
description: str
```

---
### UpdateIssueStatusRequest

```python
status: str
```

### IssueSummaryResponse

```python
id: int
room: dict | None
target_type: str
target: str | None
category: str
description: str
status: str
updated_at: datetime
```

---

### IssueDetailResponse

```python
id: int
project: dict
room: dict | None
target_type: str
target: str | None
category: str
description: str
status: str
created_by: dict
updated_by: dict
created_at: datetime
updated_at: datetime

comments: list[CommentResponse]
attachments: list[AttachmentResponse]
```

---

## 8.4 AI DTO

### GenerateDraftRequest

```python
project_id: int
target_type: str
room_id: int | None
target: str | None
input_text: str
```

---

### GenerateDraftResponse

```python
category: str
description: str
```

---

## 8.5 Comment DTO

### CreateCommentRequest

```python
comment: str
```

---

### CommentResponse

```python
id: int
comment: str
created_by: dict
created_at: datetime
```

---

## 8.6 Attachment DTO

### AttachmentResponse

```python
id: int
file_name: str
mime_type: str
file_size: int
uploaded_at: datetime
```

---

### UploadAttachmentResponse

```python
id: int
message: str
```

---

## 8.7 DTO Design Policy

DTO 設計では以下の方針を採用する。

- Request DTO と Response DTO を分離する。
- Database Model を API へ直接返却しない。
- API ごとに必要な DTO を定義する。
- 内部実装と API 仕様を分離する。
- DTO には業務ロジックを持たせない。

---

# 9. Service Design

本章では、Service Layer の設計を定義する。

Service Layer は業務ロジックを担当し、API RouterとRepository Layer の間に位置する。

---

## 9.1 Service List

|Service|責務|
|---|---|
|AuthService|認証処理|
|ProjectService|Project 取得|
|IssueService|Issue 登録・更新・参照|
|AIService|AI Draft 生成|
|CommentService|Comment 追加|
|AttachmentService|Attachment 追加・削除|
|StorageService|添付ファイル保存・削除|

---

## 9.2 AuthService

### Responsibilities

- ログイン認証
- ログアウト処理
- 現在の User 取得

### Main Methods

```python
login(username: str, password: str) -> CurrentUserResponse

logout(user_id: int) -> None

get_current_user(user_id: int) -> CurrentUserResponse
```

---

## 9.3 ProjectService

### Responsibilities

- Project 一覧取得
- Project 存在確認

### Main Methods

```python
list_projects(user_id: int) -> ProjectListResponse

validate_project_exists(project_id: int) -> None
```

---

## 9.4 IssueService

### Responsibilities

- Issue 一覧取得
- Issue 詳細取得
- Issue 登録
- Issue 更新
- Status 変更
- Project 存在確認
- Room 存在確認
- Target Type と Room / Target の整合性検証
- Category 検証
- Status 検証

### Main Methods

```python
list_issues(
    project_id: int,
    status: str | None,
    category: str | None,
    target_type: str | None,
    keyword: str | None,
    page: int,
    page_size: int
) -> list[IssueSummaryResponse]

get_issue_detail(issue_id: int) -> IssueDetailResponse

create_issue(
    project_id: int,
    request: CreateIssueRequest,
    user_id: int
) -> int

update_issue(
    issue_id: int,
    request: UpdateIssueRequest,
    user_id: int
) -> None

update_status(
    issue_id: int,
    request: UpdateIssueStatusRequest,
    user_id: int
) -> None
```

`create_issue()` は作成した Issue の ID を返却する。

API レスポンスの生成は API Router が担当する。

---

## 9.5 AIService

### Responsibilities

- 音声認識後のテキストまたは入力テキストの解析
- Ollama 呼び出し
- Category および Description の AI Draft 生成
- AI 結果の基本検証
- AI が Target Type、Room および Target を返却しないことの制御

### Main Methods

```python
generate_issue_draft(
    request: GenerateDraftRequest,
    user_id: int
) -> GenerateDraftResponse
```

AIServiceはIssueを保存しない。

---

## 9.6 CommentService

### Responsibilities

- Issue 存在確認
- Comment 追加

### Main Methods

```python
create_comment(
    issue_id: int,
    request: CreateCommentRequest,
    user_id: int
) -> int
```

Commentは編集・削除しない。

---

## 9.7 AttachmentService

### Responsibilities

- Issue 存在確認
- ファイル検証
- ファイル保存
- Attachment メタデータ登録
- Attachment 削除

### Main Methods

```python
upload_attachment(
    issue_id: int,
    file: UploadFile,
    user_id: int
) -> UploadAttachmentResponse

delete_attachment(
    issue_id: int,
    attachment_id: int,
    user_id: int
) -> None
```

---

## 9.8 StorageService

### Responsibilities

- ファイル保存
- ファイル削除
- 保存パス生成
- ファイル名生成

### Main Methods

```python
save_file(
    issue_id: int,
    file: UploadFile
) -> StoredFile

delete_file(
    file_path: str
) -> None
```

---

# 10. Repository Design

本章では、Repository Layer の設計を定義する。

Repository はデータアクセスのみを担当し、業務ロジックを持たない。

---

## 10.1 Repository List

初期版では、Hotel は Project とともに取得するため、専用の HotelRepository は定義しない。

|Repository|責務|
|---|---|
|UserRepository|User 取得|
|ProjectRepository|Project 取得（Hotel 情報を含む）|
|RoomRepository|Room 取得|
|IssueRepository|Issue 取得・登録・更新|
|CommentRepository|Comment 登録・取得|
|AttachmentRepository|Attachment 登録・取得・削除|

---

## 10.2 UserRepository

```python
find_by_id(user_id: int) -> User | None

find_by_username(username: str) -> User | None

verify_password(password: str, password_hash: str) -> bool
```

---

## 10.3 ProjectRepository

```python
find_by_id(project_id: int) -> Project | None

list_all() -> list[Project]
```

---

## 10.4 RoomRepository

```python
find_by_id(room_id: int) -> Room | None

find_by_hotel_and_room_number(
    hotel_id: int,
    room_number: str
) -> Room | None

list_by_hotel(hotel_id: int) -> list[Room]
```

初期版では Room 検索機能を提供しないため、Room 名や Room Number による検索メソッドは定義しない。

必要となった場合は追加する。

---

## 10.5 IssueRepository

Repository は永続化した Entity を返却する。

Service Layer は返却された Entity を利用して、API 用 DTO またはレスポンスデータへ変換する。

```python
find_by_id(issue_id: int) -> Issue | None

list_by_project(
    project_id: int,
    status: str | None,
    category: str |None,
    target_type: str | None,
    keyword: str | None,
    offset: int,
    limit: int
) -> list[Issue]

count_by_project(
    project_id: int,
    status: str | None,
    category: str | None,
    target_type: str | None,
    keyword: str | None
) -> int

create(issue: Issue) -> Issue

update(issue: Issue) -> Issue
```

---

## 10.6 CommentRepository

```python
list_by_issue(issue_id: int) -> list[Comment]

create(comment: Comment) -> Comment
```

---

## 10.7 AttachmentRepository

```python
find_by_id(attachment_id: int) -> Attachment | None

list_by_issue(issue_id: int) -> list[Attachment]

create(attachment: Attachment) -> Attachment

delete(attachment: Attachment) -> None
```

---

# 11. Validation Design

本章では、Service Layer で実施する Validation を定義する。

---

## 11.1 Common Validation

入力値の型や必須項目の検証は Pydantic により実施する。

Service Layer では、DB の存在確認や業務ルールなど、Pydantic では検証できない内容を検証する。

|対象|Validation|
|---|---|
|ID|対象データが存在すること|
|Required Field|必須項目が入力されていること|
|Enum|定義済み値であること|
|Permission|操作権限があること|

---

## 11.2 Issue Validation

Issue 登録・更新時には以下を検証する。

|項目|内容|
|---|---|
|Project|project_id が存在すること|
|Room|room_id が指定された場合、Room が存在すること|
|Target Type|ROOM または OTHER であること|
|Target / Room|Target Type ごとの検証ルールに従うこと（11.3参照）|
|Category|定義済み Category であること|
|Status|定義済み Status であること|
|Description|空でないこと|

---

## 11.3 Target Type Validation

Target Type は以下を許可する。

```text
ROOM
OTHER
```

|Target Type|Validation|
|---|---|
|ROOM|room_id を必須とし、target は null とする。|
|OTHER|target を必須とし、room_id は null とする。|

Database では `room_id` の NULL 制約のみを管理する。

Target Type と `room_id` および `target` の整合性は、Service Layer で検証する。

---

## 11.4 Category Validation

Category は以下を許可する。

```text
LIGHTING
SHADE
KEYPAD
SENSOR
TSTAT
PROCESSOR
NETWORK
SERVER
INTEGRATION
OTHER
```

---

## 11.5 Status Validation

Status は以下を許可する。

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

---

## 11.6 Attachment Validation

Attachment 追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_id が存在すること|
|File Type|画像または動画であること|
|File Size|許可されたサイズ以内であること|
|File Name|保存可能なファイル名であること|

---

## 11.7 Comment Validation

Comment 追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_id が存在すること|
|Comment|空でないこと|

---

# 12. Error Handling Design

本章では、Backend で利用するエラー処理方針を定義する。

---

## 12.1 Custom Exceptions

以下の共通例外を定義する。

|Exception|用途|
|---|---|
|ValidationError|入力値不正|
|AuthenticationError|認証失敗|
|AuthorizationError|権限不足|
|NotFoundError|対象データなし|
|BusinessRuleError|業務ルール違反|
|AIServiceError|AI 処理失敗|
|StorageError|ファイル保存・削除失敗|

---

## 12.2 Error Mapping

|Exception|HTTP Status|
|---|---|
|ValidationError|400|
|AuthenticationError|401|
|AuthorizationError|403|
|NotFoundError|404|
|BusinessRuleError|409|
|AIServiceError|500|
|StorageError|500|

---

## 12.3 Error Response

API では共通エラーレスポンス形式を返す。

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed."
  }
}
```

---

## 12.4 Error Message Policy

- ユーザーに理解できるメッセージを返す。
- システム内部情報を返さない。
- 詳細な例外情報はログへ記録する。

---

# 13. Authentication and Authorization Design

本章では、認証および認可の詳細設計を定義する。

---

## 13.1 Authentication Policy

認証済み User のみ API を利用できる。

未認証の場合は `401 Unauthorized` を返す。

---

## 13.2 User Roles

初期版では以下の Role を定義する。

```text
ADMINISTRATOR
ENGINEER
```

---

## 13.3 Authorization Policy

Role に応じて利用可能な機能を制御する。

|機能|Administrator|Engineer|
|---|---|---|
|Project Selection|Yes|Yes|
|Issue Management|Yes|Yes|
|AI Draft|Yes|Yes|
|Comment Management|Yes|Yes|
|Attachment Management|Yes|Yes|
|Administration|Yes|No|

---

## 13.4 API Dependency

FastAPI の Dependency で認証済み User を取得する。

```python
get_current_user() -> User
```

Role 制御が必要な API では、Role 確認用 Dependency を利用する。

```python
require_administrator(user: User) -> User
```

---

# 14. AI Service Design

本章では、AI Draft 生成機能の詳細設計を定義する。

---

## 14.1 AI Service Responsibility

AIService は Ollama を呼び出し、Issue Draft を生成する。

AIService は Category および Description を生成する。

Target Type、Room および Target は生成しない。

AIService は業務データを保存しない。

---

## 14.2 AI Draft Input

AI Draft 生成時には以下を入力とする。

|項目|説明|
|---|---|
|project_id|対象 Project|
|target_type|Target Type|
|room_id|ROOM の場合に指定する Room|
|target|OTHER の場合に指定する対象名|
|input_text|音声認識後または手入力されたテキスト|

---

## 14.3 AI Draft Output

AI Draft は以下を返却する。

|項目|説明|
|---|---|
|category|Category|
|description|Issue 内容|

---

## 14.4 AI Prompt Policy

AI への Prompt では以下を明示する。

- Category は定義済み Category のいずれかを返却する。
- Description は入力内容を自然な文章へ整形する。
- Target Type、Room および Target は推定しない。
- AI は Issue を保存しない。
- Category を判断できない場合は OTHER を返却する。

---

## 14.5 AI Error Handling

Ollama 呼び出しに失敗した場合は `AIServiceError` を発生させる。

AI 処理に失敗しても、ユーザーが手入力で Issue を登録できるようにする。

---

# 15. File Storage Design

本章では、添付ファイル保存の詳細設計を定義する。

---

## 15.1 Storage Policy

添付ファイル本体は Local Storage へ保存する。

DB には添付ファイルのメタデータのみ保存する。

---

## 15.2 Storage Directory

初期版では以下の構成を基本とする。

```text
storage/
├── attachments/
│   └── issues/
│       └── {issue_id}/
│           ├── photo_001.jpg
│           └── video_001.mp4
└── database/
```

---

## 15.3 File Path Policy

DB に保存する `file_path` は相対パスとする。

例：

```text
attachments/issues/101/photo_001.jpg
```

---

## 15.4 File Name Policy

保存時には、元ファイル名とは別に保存用ファイル名を生成する。

元ファイル名は `original_file_name` としてDBに保存する。

---

## 15.5 File Delete Policy

Attachment 削除時には以下を実施する。

1. DB の Attachment 情報を取得する。
2. Local Storage のファイルを削除する。
3. DB の Attachment 情報を削除する。

削除失敗時はエラーとして扱い、ログへ記録する。

---

# 16. Future Enhancements

将来的な拡張を以下に示す。

- Refresh Token 対応
- Password Hash 強化
- Role 追加
- Permission 単位の認可
- AI Provider 切替
- AI Prompt テンプレート管理
- 添付ファイルのサムネイル生成
- 添付ファイルのクラウド保存
- PostgreSQL 対応
- Docker 対応
- CI/CD 対応

これらは初期版の詳細設計範囲には含めない。

---

# End of Document
