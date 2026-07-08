# CIM Detailed Design

**Document Version:** 1.1
**Status:** Draft
**Last Updated:** 2026-07-03
**Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Synchronize with updated basic design and database design.|

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

本書は、CIM(Commissioning Issue Manager)の詳細設計を定義することを目的とする。

本書では、実装に必要となるバックエンド構成、レイヤー責務、DTO、Service、Repository、Validation、Error Handling、AI連携、File Storageの設計を定義する。

本書を基に、FastAPIアプリケーションの実装を行う。

---

# 2. Scope

本書では以下を対象とする。

- Backendアプリケーション構成
- ディレクトリ構成
- Layer責務
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
- DBテーブル定義
- API仕様
- UI設計
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
|api_design.md|API設計書|
|ui_design.md|UI設計書|
|project_conventions.md|プロジェクト共通ルール|
|ADR-001|User in Control|
|ADR-002|TargetType Definition|
|ADR-003|Category Definition|
|ADR-004|Room Model Design|
|ADR-005|Issue as Aggregate Root|

---

# 4. Application Architecture

本システムはFastAPIを利用したレイヤードアーキテクチャを採用する。

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

AI連携およびFile StorageはService Layerから利用する。

```text
Service
 ├── Repository
 ├── AI Client
 └── Storage Service
```

---

# 5. Backend Directory Structure

Backendのディレクトリ構成を以下に示す。

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

API RouterはHTTPリクエストを受け取り、Serviceを呼び出す。

API Routerは業務ロジックを持たない。

主な責務は以下とする。

- Request受信
- Request DTOの受け取り
- 認証済み User の取得
- Service呼び出し
- Response DTOの返却

---

## 6.2 Service Layer

Service Layerは業務ロジックを担当する。

主な責務は以下とする。

- 業務ルールの検証
- Repository呼び出し
- AI Service呼び出し
- Storage Service呼び出し
- トランザクション単位の制御
- Domain ModelとDTOの変換補助

---

## 6.3 Repository Layer

Repository Layerはデータアクセスを担当する。

Repositoryは業務ロジックを持たない。

主な責務は以下とする。

- データ取得
- データ登録
- データ更新
- データ削除
- 検索条件に基づくQuery実行

---

## 6.4 Models

ModelsはDBテーブルに対応するSQLAlchemyモデルを定義する。

---

## 6.5 Schemas

SchemasはPydanticを利用したDTOを定義する。

主な用途は以下とする。

- Request DTO
- Response DTO
- Internal DTO

---

## 6.6 Core

Coreにはアプリケーション全体で利用する共通機能を配置する。

例：

- 設定
- Security
- 共通例外
- 共通エラー定義

---

# 7. Domain Models

本章では、システムで利用するドメインモデルを定義する。

ドメインモデルは業務上の概念を表現し、SQLAlchemy Modelとは役割を分離する。

初期版では、RepositoryがSQLAlchemy Modelを扱い、Service Layerがドメインルールを適用する。

---

## 7.1 Domain Model Overview

本システムで扱う主要なドメインモデルを以下に示す。

|Domain Model|説明|
|---|---|
|User|システム利用者 (username、password_hash、display_name、role)|
|Hotel|ホテル・施設|
|Project|コミッショニング案件|
|RoomType|部屋種別|
|Room|Hotel に属する部屋|
|Issue|Project に属し、必要に応じて Room を参照する課題|
|Comment|Issue へのコメント|
|Attachment|Issue への添付ファイル|

---

## 7.2 Aggregate

本システムではIssueをAggregate Rootとする。

```text
Issue
 ├── Comment
 └── Attachment
```

CommentおよびAttachmentは必ずIssueに属する。

単独では生成・管理しない。

---

## 7.3 Domain Responsibilities

|Domain|主な責務|
|---|---|
|User|利用者情報|
|Hotel|Hotel管理|
|Project|Project管理|
|RoomType|Room分類|
|Room|Room管理|
|Issue|Issue管理の中心|
|Comment|コメント履歴|
|Attachment|添付ファイル管理|

---

# 8. DTO Design

本章では、APIで利用するDTO(Data Transfer Object)を定義する。

DTOはPydantic Modelとして実装する。

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
hotel_name: str
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
target: str
category: str
description: str
```

---

### UpdateIssueRequest

```python
room_id: int | None
target_type: str
target: str
category: str
description: str
status: str
```

---

### IssueSummaryResponse

```python
id: int
room: str | None
target_type: str
target: str
category: str
description: str
status: str
updated_at: datetime
```

---

### IssueDetailResponse

```python
id: int
project_id: int
room_id: int | None
target_type: str
target: str
category: str
description: str
status: str
created_by: str
created_at: datetime
updated_at: datetime

comments: list
attachments: list
```

---

## 8.4 AI DTO

### GenerateDraftRequest

```python
project_id: int
input_text: str
```

---

### GenerateDraftResponse

```python
target_type: str
target: str
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
created_by: str
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

DTO設計では以下の方針を採用する。

- Request DTOとResponse DTOを分離する。
- Database ModelをAPIへ直接返却しない。
- APIごとに必要なDTOを定義する。
- 内部実装とAPI仕様を分離する。
- DTOには業務ロジックを持たせない。

---

# 9. Service Design

本章では、Service Layerの設計を定義する。

Service Layerは業務ロジックを担当し、API RouterとRepository Layerの間に位置する。

---

## 9.1 Service List

|Service|責務|
|---|---|
|AuthService|認証処理|
|ProjectService|Project取得|
|IssueService|Issue登録・更新・参照|
|AIService|AI Draft生成|
|CommentService|Comment追加|
|AttachmentService|Attachment追加・削除|
|StorageService|添付ファイル保存・削除|

---

## 9.2 AuthService

### Responsibilities

- ログイン認証
- ログアウト処理
- 現在のUser取得

### Main Methods

```python
login(username: str, password: str) -> CurrentUserResponse

logout(user_id: int) -> None

get_current_user(user_id: int) -> CurrentUserResponse
```

---

## 9.3 ProjectService

### Responsibilities

- Project一覧取得
- Project存在確認

### Main Methods

```python
list_projects(user_id: int) -> ProjectListResponse

validate_project_exists(project_id: int) -> None
```

---

## 9.4 IssueService

### Responsibilities

- Issue一覧取得
- Issue詳細取得
- Issue登録
- Issue更新
- Status変更
- Room 指定時の存在確認
- Room 未指定 Issue の登録・更新許可
- TargetType整合性検証
- Category検証
- Status検証

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
    status: str,
    user_id: int
) -> None
```

---

## 9.5 AIService

### Responsibilities

- 入力テキスト解析
- Ollama呼び出し
- AI Draft生成
- AI結果の基本検証

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

- Issue存在確認
- Comment追加

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

- Issue存在確認
- ファイル検証
- ファイル保存
- Attachmentメタデータ登録
- Attachment削除

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

本章では、Repository Layerの設計を定義する。

Repositoryはデータアクセスのみを担当し、業務ロジックを持たない。

---

## 10.1 Repository List

|Repository|責務|
|---|---|
|UserRepository|User取得|
|ProjectRepository|Project取得|
|RoomRepository|Room取得|
|IssueRepository|Issue取得・登録・更新|
|CommentRepository|Comment登録・取得|
|AttachmentRepository|Attachment登録・取得・削除|

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

find_by_project_and_room_number(
    project_id: int,
    room_number: str
) -> Room | None

list_by_project(project_id: int) -> list[Room]
```

---

## 10.5 IssueRepository

```python
find_by_id(issue_id: int) -> Issue | None

list_by_project(
    project_id: int,
    status: str | None,
    category: str | None,
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

本章では、Service Layerで実施するValidationを定義する。

---

## 11.1 Common Validation

|対象|Validation|
|---|---|
|ID|対象データが存在すること|
|Required Field|必須項目が入力されていること|
|Enum|定義済み値であること|
|Permission|操作権限があること|

---

## 11.2 Issue Validation

Issue登録・更新時には以下を検証する。

|項目|内容|
|---|---|
|Project|project_id が存在すること|
|Room|room_id が指定された場合、Room が存在すること|
|TargetType|定義済み TargetType であること|
|Category|定義済み Category であること|
|Status|定義済み Status であること|
|Description|空でないこと|

---

## 11.3 TargetType Validation

TargetTypeは以下を許可する。

```text
ROOM
ROOM_TYPE
AREA
HOTEL
GENERAL
```

初期版では、Issue登録画面で選択されたTargetTypeを保存する。

TargetTypeごとの詳細整合性は、必要に応じてService Layerで検証する。

---

## 11.4 Category Validation

Categoryは以下を許可する。

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

Statusは以下を許可する。

```text
OPEN
IN_PROGRESS
COMPLETED
```

---

## 11.6 Attachment Validation

Attachment追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_idが存在すること|
|File Type|画像または動画であること|
|File Size|許可されたサイズ以内であること|
|File Name|保存可能なファイル名であること|

---

## 11.7 Comment Validation

Comment追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_idが存在すること|
|Comment|空でないこと|

---

# 12. Error Handling Design

本章では、Backendで利用するエラー処理方針を定義する。

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
|AIServiceError|AI処理失敗|
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

APIでは共通エラーレスポンス形式を返す。

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

- 利用者に理解できるメッセージを返す。
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

初期版では以下のRoleを定義する。

```text
ADMINISTRATOR
ENGINEER
```

---

## 13.3 Authorization Policy

Roleに応じて利用可能な機能を制御する。

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

FastAPIのDependencyで認証済みUserを取得する。

```python
get_current_user() -> User
```

Role制御が必要なAPIでは、Role確認用Dependencyを利用する。

```python
require_administrator(user: User) -> User
```

---

# 14. AI Service Design

本章では、AI Draft生成機能の詳細設計を定義する。

---

## 14.1 AI Service Responsibility

AIServiceはOllamaを呼び出し、Issue Draftを生成する。

AIServiceは業務データを保存しない。

---

## 14.2 AI Draft Input

AI Draft生成時には以下を入力とする。

|項目|説明|
|---|---|
|project_id|対象Project|
|input_text|音声認識後または手入力されたテキスト|

---

## 14.3 AI Draft Output

AI Draftは以下を返却する。

|項目|説明|
|---|---|
|target_type|TargetType|
|target|対象|
|category|Category|
|description|Issue内容|

---

## 14.4 AI Prompt Policy

AIへのPromptでは以下を明示する。

- TargetTypeは定義済み値から選択する。
- Categoryは定義済み値から選択する。
- DescriptionはIssue内容として自然な文章に整形する。
- AIはIssueを保存しない。
- 判断が難しい場合はGENERALまたはOTHERを使用する。

---

## 14.5 AI Error Handling

Ollama呼び出しに失敗した場合は `AIServiceError` を発生させる。

AI処理に失敗しても、利用者が手入力でIssueを登録できるようにする。

---

# 15. File Storage Design

本章では、添付ファイル保存の詳細設計を定義する。

---

## 15.1 Storage Policy

添付ファイル本体はLocal Storageへ保存する。

DBには添付ファイルのメタデータのみ保存する。

---

## 15.2 Storage Directory

初期版では以下の構成を基本とする。

```text
storage/
└── attachments/
    └── issues/
        └── {issue_id}/
            ├── photo_001.jpg
            └── video_001.mp4
```

---

## 15.3 File Path Policy

DBに保存する `file_path` は相対パスとする。

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

Attachment削除時には以下を実施する。

1. DBのAttachment情報を取得する。
2. Local Storageのファイルを削除する。
3. DBのAttachment情報を削除する。

削除失敗時はエラーとして扱い、ログへ記録する。

---

# 16. Future Enhancements

将来的な拡張を以下に示す。

- Refresh Token対応
- Password Hash強化
- Role追加
- Permission単位の認可
- AI Provider切替
- AI Promptテンプレート管理
- 添付ファイルのサムネイル生成
- 添付ファイルのクラウド保存
- PostgreSQL対応
- Docker対応
- CI/CD対応

これらは初期版の詳細設計範囲には含めない。

---

# End of Document
