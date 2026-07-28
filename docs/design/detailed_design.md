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
│   ├── clients/
│   │   ├── __init__.py
│   │   └── ollama_client.py
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

## 7.4 ORM Mapping Policy

SQLAlchemy Model は SQLAlchemy 2.x の型付き ORM を使用する。

Role、Target Type、Category および Status は Python Enum として定義し、DB には Enum の文字列値を保存する。

`relationship` には必要に応じて `back_populates` を使用する。

初期版では、`relationship` に削除 cascade および `delete-orphan` を設定しない。

Foreign Key には `ON DELETE` を指定しない。

Issue の `created_by` と `updated_by` のように同一テーブルを複数回参照する場合は、`relationship` の `foreign_keys` を明示する。

---

## 7.5 Timestamp Policy

Timestamp は UTC で管理する。

アプリケーション内では UTC の timezone-aware datetime を生成する。

SQLite へ保存する際は timezone 情報を除去し、UTC を表す timezone-naive datetime として保存する。

DB から取得した timezone-naive datetime は UTC として扱う。

`created_at`、`updated_at` および `uploaded_at` は Python 側で設定する。

`updated_at` は Service Layer の更新処理で明示的に更新する。

DB の `server_default` および ORM Event による自動更新は使用しない。

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
file_name: str
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

- Username による User 取得
- Password Hash の検証
- ログイン認証
- 現在の User 取得

### Main Methods

```python
login(username: str, password: str) -> CurrentUserResponse

get_current_user(user_id: int) -> CurrentUserResponse
```

`login()` は `UserRepository.find_by_username()` を使用して User を取得し、
`app/core/security.py` の Password verification 処理を使用して Password を検証する。

Username が存在しない場合と Password が一致しない場合は、いずれも `AuthenticationError` とする。
外部へ返すエラー内容から、Username の存在有無を判別できないようにする。

`get_current_user()` で指定された User が存在しない場合は、認証情報が無効であるものとして `AuthenticationError` とする。

認証状態は API Layer が Cookie-based Session として管理する。

AuthService は HTTP Request、Cookie または Session を直接扱わない。

Login 成功後の Session 作成および Logout 時の Session 削除は API Layer の責務とする。

そのため `logout()` は AuthService には実装しない。

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

Issue 新規登録時の初期 Status は `OPEN` とする。
`CreateIssueRequest` では Status を受け取らず、`IssueService.create_issue()` が `Status.OPEN` を設定する。
Model または Database の default には依存しない。

API レスポンスの生成は API Router が担当する。

---

## 9.5 AIService

### Responsibilities

- Project 存在確認
- Target Type と Room / Target の整合性検証
- Room 存在確認および Project の Hotel との整合性検証
- 入力テキストの検証
- Ollama Client 呼び出し
- Category および Description の AI Draft 生成
- AI 結果の検証
- AI が Target Type、Room および Target を返却しないことの制御
- Ollama 処理失敗時の `AIServiceError` への変換

### Main Methods

```python
generate_issue_draft(
    request: GenerateDraftRequest,
    user_id: int
) -> GenerateDraftResponse
```

AIService は Issue を保存しない。

`generate_issue_draft()` では、Project の存在、Target Type と Room / Target の整合性、および入力テキストを検証してから Ollama Client を呼び出す。

Target Type の検証ルールは Issue 登録時と同じく以下とする。

- `ROOM`: `room_id` を必須とし、`target` は `None` とする。
- `OTHER`: `room_id` は `None` とし、`target` を必須とする。

`ROOM` の場合は Room が存在し、その Room が Project と同じ Hotel に属することを検証する。

`input_text` が空文字の場合は `ValidationError` とする。
入力値を trim、翻訳、正規化または補完しない。

`user_id` は後続の認証済み API から渡される値であり、本 Service では User の再取得や認可判定には使用しない。

AIService は SQLAlchemy Session を保持せず、commit および rollback を行わない。

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
- User 存在確認
- ファイル名、ファイル形式、ファイルサイズの検証
- StorageService を使用したファイル保存
- Attachment メタデータ登録
- Upload 失敗時のファイル補償削除
- Attachment と Issue の所属確認
- StorageService を使用した Attachment 削除
- DB と Local Storage の整合性制御

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

`upload_attachment()` および `delete_attachment()` では User の存在を確認する。

`delete_attachment()` の `user_id` は初期版では User 存在確認にのみ使用し、削除者の監査情報や認可判定には使用しない。

AttachmentService は DB Transaction を管理する。

Repository は commit / rollback を行わない。

---

## 9.8 StorageService

### Responsibilities

- ファイル保存
- ファイル削除
- 削除対象ファイルの一時退避
- 一時退避ファイルの復元
- 保存パス生成
- 保存用ファイル名生成
- Storage Root 外へのパスアクセス防止

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

DB 削除との整合性制御に必要な一時退避・復元処理は StorageService の内部責務とする。

`StoredFile` は Storage Layer 内部で使用するデータ構造とし、以下を保持する。

```python
@dataclass(frozen=True)
class StoredFile:
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
```

`file_path` は Storage Root からの相対パスとする。

`StoredFile` は API の公開 DTO として使用しない。

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

Database では `room_id` および `target` の個別の NULL 許可のみを管理する。

Target Type と `room_id` および `target` の整合性は、Service Layer で検証する。

Target Type と `room_id` および `target` の組み合わせを検証する複合 CHECK 制約は Database に定義しない。

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

Password は平文では保存せず、Password Hash として保存する。

Password hashing には `pwdlib` を使用し、Argon2 対応を有効化する。

Password hashing および verification には `PasswordHash.recommended()` を使用する。

Password hashing の具体的なパラメーターは `pwdlib` の recommended configuration に従い、アプリケーション側では個別に固定しない。

Password hashing および verification の処理は `app/core/security.py` に集約する。

認証状態の保持には Cookie-based Session を使用する。

HTTP Session の実装には Starlette の `SessionMiddleware` を使用する。

Session には認証済み User の `user_id` のみを保持する。

```python
{
    "user_id": 1
}
```

Username、Role、Password Hash などの User 情報は Session に保持しない。

認証済み User 情報が必要な場合は、Session から取得した `user_id` を使用して `AuthService.get_current_user()` から取得する。

JWT、Bearer Token、Refresh Token および Server-side Session Database は初期版では使用しない。

---

## 13.2 Session Configuration

Session Cookie の設定を以下とする。

|設定|値|
|---|---|
|Cookie Name|`cim_session`|
|Session Data|`user_id` のみ|
|HttpOnly|`True`|
|SameSite|`lax`|
|Secure|`False`|
|Path|`/`|
|Max Age|8時間|

Session の署名に使用する Secret は `app/core/config.py` で管理する。

|設定|環境変数|Default|
|---|---|---|
|Session Secret|`CIM_SESSION_SECRET`|なし|

`CIM_SESSION_SECRET` は必須設定とし、未設定の場合はアプリケーションを起動しない。

Session Secret をソースコードへ固定しない。

初期版はローカル LAN 上の HTTP 環境での利用を想定するため、Session Cookie の `Secure` は `False` とする。

HTTPS 環境へ移行する場合は `Secure=True` へ変更する。

Session 有効期間は8時間とする。

8時間経過後は再認証を必要とする。

---

## 13.3 User Roles

初期版では以下の Role を定義する。

```text
ADMINISTRATOR
ENGINEER
```

---

## 13.4 Authorization Policy

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

## 13.5 API Dependency

FastAPI の Dependency で認証済み User を取得する。

Authentication Dependency は Request の Session から `user_id` を取得する。

Session に `user_id` が存在しない場合は `AuthenticationError` とし、API では `401 Unauthorized` を返す。

Session に `user_id` が存在する場合は、`AuthService.get_current_user(user_id)` を使用して現在の User 情報を取得する。

```python
get_current_user() -> CurrentUserResponse
```

Session に保存された `user_id` に対応する User が存在しない場合も、認証状態が無効であるものとして `AuthenticationError` とする。

API Router は Dependency から取得した `CurrentUserResponse.id` を、必要に応じて各 Service の `user_id` として渡す。

Authentication Dependency は以下を行わない。

- Password verification
- Role authorization
- Database への直接 Query
- Session の作成
- Session の削除

Role 制御が必要な API では、Authentication とは別の Role 確認用 Dependency を利用する。

```python
require_administrator(
    user: CurrentUserResponse
) -> CurrentUserResponse
```

---

## 13.6 Authentication API Session Flow

### Login

`POST /api/auth/login` では以下の順序で処理する。

1. Login Request から Username と Password を取得する。
2. `AuthService.login()` を呼び出す。
3. 認証成功時、Session に認証済み User の `id` を `user_id` として保存する。
4. Login Response を返す。

```python
request.session["user_id"] = current_user.id
```

認証失敗時は Session を作成せず、`401 Unauthorized` を返す。

### Current User

`GET /api/auth/me` では Authentication Dependency を使用する。

1. Session から `user_id` を取得する。
2. `AuthService.get_current_user(user_id)` を呼び出す。
3. `CurrentUserResponse` を返す。

Session が存在しない場合、または Session 内の `user_id` が無効な場合は `401 Unauthorized` を返す。

### Logout

`POST /api/auth/logout` では Authentication Dependency により認証済みであることを確認した後、Session を削除する。

```python
request.session.clear()
```

Logout は API Layer の責務とし、`AuthService.logout()` は定義しない。

Logout 成功後、それまで使用していた Session では認証済み API を利用できない。

---

## 13.7 CSRF Policy

初期版では Frontend と Backend を同一 Origin で提供する。

Session Cookie は `SameSite=lax` とする。

初期版では専用の CSRF Token は導入しない。

状態を変更する API は `POST`、`PUT`、`PATCH`、`DELETE` 等の適切な HTTP Method を使用し、GET Request では業務データを変更しない。

CORS で任意の Origin を許可しない。

将来、Frontend と Backend を別 Origin で運用する場合、または外部ネットワークへ公開する場合は、CSRF 対策および Cookie Policy を再検討する。

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

Ollama への Prompt は System Message と User Message に分離する。

System Message では以下を明示する。

- CIM の Issue Draft 生成支援であること。
- 出力は Category と Description のみとすること。
- Category は定義済み Category のいずれかとすること。
- Description は入力内容を自然な Issue 文へ整形すること。
- 入力に存在しない事実を追加しないこと。
- Target Type、Room および Target を推定または変更しないこと。
- AI は Issue を保存しないこと。
- Category を判断できない場合は `OTHER` を返却すること。

User Message には以下を入力する。

- ユーザーが選択した Target Type
- `ROOM` の場合は選択済み Room の Room Number
- `OTHER` の場合は選択済み Target
- `input_text`

`project_id` および User 情報は Prompt に含めない。

Target Type、Room および Target は Description 生成の文脈としてのみ使用し、AI の出力項目には含めない。

---

## 14.5 AI Error Handling

以下の場合は `AIServiceError` とする。

- Ollama への接続失敗
- Ollama 呼び出しの timeout
- Ollama がエラーレスポンスを返した場合
- Ollama のレスポンスが期待する Structured Output として解析できない場合
- Category が定義済み Category に含まれない場合
- Description が欠落している場合
- Description が文字列でない場合
- Description が空文字の場合
- AI 利用時に Ollama Model が設定されていない場合

不正な Category をアプリケーション側で `OTHER` へ変換しない。

`OTHER` は AI が Category を判断できない場合に返すよう Prompt で指示する値であり、任意の不正出力に対する fallback ではない。

Ollama の endpoint、内部例外、Prompt、Provider Response などの内部情報は利用者向けエラーメッセージへ含めない。

AI 処理に失敗しても、ユーザーが手入力で Issue を登録できるようにする。

---

## 14.6 Ollama Integration

Ollama との通信には公式 `ollama` Python Client を使用する。

初期版では同期 `Client` と `chat()` を使用する。

Streaming は使用しない。

Ollama の設定は `app/core/config.py` で管理する。

|設定|環境変数|Default|
|---|---|---|
|Host|`CIM_OLLAMA_HOST`|`http://localhost:11434`|
|Model|`CIM_OLLAMA_MODEL`|なし|
|Timeout|`CIM_OLLAMA_TIMEOUT_SECONDS`|`60` 秒|

Model は環境ごとに変更可能とし、アプリケーションコードへ固定しない。

`CIM_OLLAMA_MODEL` が設定されていない場合でもアプリケーション自体は起動可能とする。
AI Draft 利用時に Model が未設定の場合は `AIServiceError` とする。

Ollama Client は `app/clients/ollama_client.py` に配置し、Provider との通信のみを担当する。

AIService は Ollama 固有の通信処理を直接実装しない。

Ollama へのリクエストでは以下を使用する。

- Operation: `chat()`
- Streaming: `False`
- Temperature: `0`
- Response Format: JSON Schema による Structured Output

Structured Output 用の内部 Pydantic Model を定義し、以下の2項目のみを受け取る。

```python
category: Category
description: str
```

Structured Output の JSON Schema は Pydantic Model の `model_json_schema()` から生成する。

Ollama が返した Message Content は Pydantic で検証してから `GenerateDraftResponse` へ変換する。

---

# 15. File Storage Design

本章では、添付ファイル保存の詳細設計を定義する。

---

## 15.1 Storage Policy

添付ファイル本体は Local Storage へ保存する。

DB には添付ファイルのメタデータのみ保存する。

---

## 15.2 Storage Directory

Local Storage Root は `app/core/config.py` で管理する。

|設定|環境変数|Default|
|---|---|---|
|Storage Root|`CIM_STORAGE_ROOT`|`./storage`|

`CIM_STORAGE_ROOT` が相対パスの場合は、Backend プロセスの Current Working Directory を基準として解決する。

初期版では Attachment を以下の構成で保存する。

```text
storage/
├── attachments/
│   └── issues/
│       └── {issue_id}/
│           └── {generated_file_name}
├── .trash/
└── database/
```

DB には Storage Root を含まない相対パスのみ保存する。

テストでは実際の Storage Root を使用せず、一時ディレクトリを使用する。

---

## 15.3 File Path Policy

DB に保存する `file_path` は Storage Root からの相対パスとする。

保存形式は以下とする。

```text
attachments/issues/{issue_id}/{generated_file_name}
```

例：

```text
attachments/issues/101/550e8400-e29b-41d4-a716-446655440000.jpg
```

StorageService は、解決後の物理パスが必ず Storage Root 配下であることを確認する。

Client から受け取ったファイル名を保存パスとして直接使用しない。

絶対パスおよび `..` 等による Storage Root 外への Path Traversal を許可しない。

---

## 15.4 File Name Policy

保存用ファイル名は UUID v4 と元ファイルの許可済み拡張子を組み合わせて生成する。

形式：

```text
{uuid_v4}{extension}
```

例：

```text
550e8400-e29b-41d4-a716-446655440000.jpg
```

UUID v4 により、同名ファイルおよび同時アップロード時の衝突を回避する。

拡張子は小文字へ正規化する。

元ファイル名は `original_file_name` として DB に保存する。

元ファイル名は以下を満たす必要がある。

- `None` ではない
- 空文字ではない
- ファイル名のみであり、ディレクトリ部分を含まない
- 絶対パスではない
- `/` または `\` を含まない
- 制御文字を含まない
- 許可済み拡張子を持つ

条件を満たさない場合は `ValidationError` とする。

---

## 15.5 File Type Policy

初期版で保存を許可するファイル形式は以下とする。

|種別|MIME Type|拡張子|
|---|---|---|
|JPEG Image|`image/jpeg`|`.jpg`, `.jpeg`|
|PNG Image|`image/png`|`.png`|
|MP4 Video|`video/mp4`|`.mp4`|
|QuickTime Video|`video/quicktime`|`.mov`|

ファイル形式の検証では、アップロード時に受け取った MIME Type と元ファイル名の拡張子の両方を確認する。

拡張子は大文字・小文字を区別せずに判定し、保存時には小文字へ正規化する。

MIME Type と拡張子は、上記の表で対応する組み合わせでなければならない。

例えば以下は有効とする。

```text
image/jpeg + .jpg
image/jpeg + .jpeg
image/png + .png
video/mp4 + .mp4
video/quicktime + .mov
```

許可されていない MIME Type、許可されていない拡張子、または MIME Type と拡張子の組み合わせが一致しない場合は `ValidationError` とする。

初期版ではファイル内容のシグネチャ解析による形式判定は行わない。

MIME Type はアップロード時に受け取った値を使用し、許可済みの MIME Type として検証した後、Attachment の `mime_type` として DB に保存する。

---

## 15.6 File Size Policy

ファイルサイズ制限を以下とする。

|種別|最大サイズ|
|---|---:|
|Image|10 MiB|
|Video|100 MiB|

1 MiB は `1024 * 1024` bytes とする。

0 byte のファイルは許可しない。

ファイルサイズは実際に読み取った byte 数から算出し、DB の `file_size` に保存する。

制限を超える場合は `ValidationError` とし、Local Storage へ保存しない。

---

## 15.7 File Delete Policy

Attachment 削除時には以下を実施する。

1. Issue の存在を確認する。
2. User の存在を確認する。
3. DB の Attachment 情報を取得する。
4. Attachment が指定 Issue に属することを確認する。
5. Local Storage の対象ファイルを同一 Storage Root 内の `.trash/` へ一時移動する。
6. DB の Attachment 情報を削除する。
7. DB Transaction を commit する。
8. `.trash/` の一時ファイルを完全削除する。

物理ファイルの一時移動後、DB 削除または commit に失敗した場合は、DB Transaction を rollback し、一時ファイルを元の場所へ復元する。

対象の物理ファイルが既に存在しない場合は、物理ファイルは既に削除済みとみなし、DB の Attachment 情報の削除を継続する。

DB commit 後の `.trash/` 完全削除に失敗した場合は `StorageError` としてログへ記録する。

この場合、Attachment は利用者から見て削除済みであり、残存する `.trash/` ファイルは内部 Storage の孤立ファイルとして扱う。

初期版では自動 Recovery Queue は実装しない。

---

## 15.8 Upload Compensation Policy

Attachment Upload では以下の順序で処理する。

1. Issue の存在を確認する。
2. User の存在を確認する。
3. ファイルを検証する。
4. Local Storage へファイルを保存する。
5. Attachment メタデータを Repository へ登録する。
6. DB Transaction を commit する。

Local Storage への保存に失敗した場合は DB 登録を行わない。

ファイル保存後に Attachment メタデータ登録または DB commit が失敗した場合は、DB Transaction を rollback し、保存済みファイルを削除する。

補償削除にも失敗した場合は `StorageError` とし、元の DB 例外より補償失敗を外部へ報告する。

DB Transaction は rollback された状態を維持する。

削除できなかった物理ファイルは孤立ファイルとして残る可能性があるため、内部ログへ記録する。

初期版では孤立ファイルの自動回収処理や Recovery Queue は実装しない。

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
