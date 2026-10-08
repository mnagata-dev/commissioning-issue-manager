# CIM Detailed Design

- **Document Version:** 1.4
- **Status:** Draft
- **Last Updated:** 2026-10-08
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Synchronize with updated basic design and database design.|
|1.2|2026-07-09|Align with Requirements v1.2, Database Design, API Design, and UI Design. Simplify Target Type, update AI Draft design, validation rules, and related service definitions.|
|1.3|2026-09-29|Align with Requirements, Basic Design, API Design and UI Design v1.3, and updated ADR-001. Define Local Speech Recognition and SpeechService responsibilities separately from AI Draft generation.|
|1.3|2026-09-30|Define whisper-cli invocation, audio normalization with ffmpeg, temporary file handling, and executable/model path configuration.|
|1.3|2026-10-07|Define Project-scoped localStorage persistence, restoration, and failure handling for Input Assistance.|
|1.4|2026-10-08|Define Administration CLI, service validation, repository writes, bootstrap, and Administrator protection in line with Requirements v1.4.|

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
- Administration CLI
- AI Service
- Speech Service / Local Speech Recognition
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

Administration CLI は以下の構成とし、HTTP API を経由しない。

```text
CLI → AdministrationService → Repository → SQLite
```

CLI は引数解析、非表示入力、依存関係の組み立て、結果表示および終了コードへの変換を担当する。認証・認可、入力検証、業務ルールおよび Transaction 管理は AdministrationService が担当する。

AI 連携および File Storage は Service Layer から利用する。

```text
Service
 ├── Repository
 ├── AI Client
 └── Storage Service
```

音声文字起こしと AI Draft 生成は、以下の独立したフローとする。

```text
Speech Transcription:
Frontend → API Router → SpeechService → Local Speech Recognition

AI Draft:
Frontend → API Router → AIService → Ollama Client → Ollama
```

SpeechService は AIService を呼び出さない。文字起こし結果は Speech API のレスポンスとして Frontend に返し、既存の Voice / Text Input に表示する。

ユーザーは文字起こし結果を必要に応じて修正するか、Voice / Text Input に直接テキストを入力する。文字起こし結果の確認・修正を独立した必須操作とはしない。

ユーザーが Generate AI Draft を実行すると、Frontend は Voice / Text Input のテキストを既存の `POST /api/ai/issue-draft` に送信する。テキスト直接入力では Local Speech Recognition を経由しない。

生成された Category と日本語 Description はユーザーが確認し、必要に応じて修正した後、Save により Issue を登録する。AI は Issue を自動登録しない（User in Control）。

---

# 5. Backend Directory Structure

Backend のディレクトリ構成を以下に示す。

```text
backend/
├── app/
│   ├── main.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── __main__.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   └── speech_client.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── projects.py
│   │       ├── rooms.py
│   │       ├── issues.py
│   │       ├── ai.py
│   │       ├── speech.py
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
│   │   ├── administration.py
│   │   ├── project.py
│   │   ├── room.py
│   │   ├── issue.py
│   │   ├── ai.py
│   │   ├── speech.py
│   │   ├── comment.py
│   │   └── attachment.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── administration_service.py
│   │   ├── project_service.py
│   │   ├── room_service.py
│   │   ├── issue_service.py
│   │   ├── ai_service.py
│   │   ├── speech_service.py
│   │   ├── comment_service.py
│   │   ├── attachment_service.py
│   │   └── storage_service.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── hotel_repository.py
│   │   ├── room_type_repository.py
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

# 6. Frontend Architecture

## 6.1 Frontend Directory Structure

Frontend はリポジトリ直下の `frontend/` に配置する。

初期構成を以下に示す。

```text
frontend/
├── index.html
├── projects.html
├── issues.html
├── issue.html
├── css/
│   └── style.css
└── js/
    ├── api.js
    ├── auth.js
    ├── login.js
    ├── projects.js
    ├── issues.js
    └── issue.js
```

Frontend は HTML、CSS および JavaScript で構成する。

React、TypeScript、npm および build tool は初期版では使用しない。

## 6.2 Frontend Delivery

Frontend は既存の FastAPI アプリケーションから配信する。

Frontend と Backend は同一 Origin とする。

画面および静的ファイルの配信先を以下に示す。

|URL|配信対象|
|---|---|
|`/`|`frontend/index.html`|
|`/projects.html`|`frontend/projects.html`|
|`/issues.html`|`frontend/issues.html`|
|`/issue.html`|`frontend/issue.html`|
|`/css/*`|`frontend/css/*`|
|`/js/*`|`frontend/js/*`|

HTML は `FileResponse` を使用して返却する。

CSS および JavaScript は FastAPI の `StaticFiles` を使用して配信する。

Frontend の画面ルートは OpenAPI Schema に含めない。

既存の `/api/*` REST API のパスおよび動作は変更しない。

別の Frontend Server、npm development server または reverse proxy は初期版では導入しない。

---

## 6.3 Input Assistance

Requirements v1.3 §7.12 および UI Design §12.7 の入力支援は Frontend で実現する。新しい API や Database Schema は追加しない。

### Stored Data

ブラウザの localStorage に、Project ID で区別して以下を保存する。他の Project の値や履歴は使用しない。

|保存対象|内容|
|---|---|
|前回利用値|Issue 登録に使用した Target Type、Room（room_id）、Category|
|OTHER Target 入力履歴|Target Type = OTHER の Issue 登録に使用した Target|

### Save and Restore

Issue Create の登録成功後に、その Issue が属する Project の前回利用値を保存する。Target Type が OTHER の場合だけ、その Target を同じ Project の履歴へ追加する。登録失敗、入力中、キャンセル、AI Draft 生成では保存しない。

Issue Create を開いたときは、現在選択中の Project の保存値を読み込む。Target Type と Category は現在選択可能な値であることを確認し、Room は現在の Project の選択可能な Room に含まれることを確認してから、UI Design §12.7 に従って復元する。保存値が存在しない、無効、または現在利用できない場合は、その項目を復元しない。

OTHER Target 入力履歴も現在の Project のものだけを読み込み、Target Type = OTHER のとき候補として表示する。候補の選択・自由入力はユーザーが行い、AI に Target の推測・自動決定をさせない。

Issue Edit は編集対象 Issue の現在値を初期表示し、前回利用値を適用しない。更新成功時も、前回利用値および OTHER Target 入力履歴は保存・更新しない。

### localStorage Errors

localStorage の読み込み・書き込み、および保存データの解析で発生するエラーは入力支援処理内で扱う。読み込めない値や履歴は適用せず、通常の初期状態とする。

localStorage が利用できない場合でも、通常の入力・Issue 登録処理を継続する。登録成功後の保存エラーによって、成功した Issue 登録を失敗として扱わない。入力支援だけを利用できない状態とする。

---

# 7. Layer Responsibilities

## 7.1 API Router

API Router は HTTP リクエストを受け取り、Service を呼び出す。

API Router は業務ロジックを持たない。

主な責務は以下とする。

- Request 受信
- Request DTO の受け取り
- 認証済み User の取得
- Service 呼び出し
- Response DTO の返却

### Speech API Router

`app/api/routes/speech.py` は `POST /api/speech/transcriptions` を担当する。

- 既存の Authentication Dependency により認証済みリクエストを受け付ける。
- `multipart/form-data` の `audio` を受け取る。
- SpeechService を呼び出す。
- transcription text を `SpeechTranscriptionResponse` として返す。
- Service の例外は第13章の共通エラーハンドリング方針に従って扱う。

Project、Target Type、Room、Target の決定、Category / Description および AI Draft の生成、Issue の登録・更新は行わない。

---

## 7.2 Service Layer

Service Layer は業務ロジックを担当する。

主な責務は以下とする。

- 業務ルールの検証
- Repository 呼び出し
- AI Service 呼び出し
- Storage Service 呼び出し
- トランザクション単位の制御
- Domain Model と DTO の変換補助

初期版では、1 API リクエストを 1 トランザクションとして処理する。

ただし Speech Transcription は DB を利用せず、SpeechService に SQLAlchemy Session や Repository を必要としない。SpeechService は audio の基本的な検証、Local Speech Recognition の呼び出し、結果の検証、失敗時のアプリケーション例外への変換、および transcription text の返却を担当する（10.10参照）。

---

## 7.3 Repository Layer

Repository Layer はデータアクセスを担当する。

Repository は業務ロジックを持たない。

主な責務は以下とする。

- データ取得
- データ登録
- データ更新
- データ削除
- 検索条件に基づく Query 実行

---

## 7.4 Models

Models は DB テーブルに対応する SQLAlchemy モデルを定義する。

---

## 7.5 Schemas

Schemas は Pydantic を利用した DTO を定義する。

主な用途は以下とする。

- Request DTO
- Response DTO
- Internal DTO

---

## 7.6 Core

Core にはアプリケーション全体で利用する共通機能を配置する。

例：

- 設定
- Security
- 共通例外
- 共通エラー定義

---

## 7.7 Local Speech Recognition Boundary

`app/clients/speech_client.py` は Local Speech Recognition との境界とし、SpeechService から利用する。

- audio を受け取り、ローカル環境で文字起こしして text を返す。
- 必要なモデルと実行環境はローカルで利用可能とし、インターネット接続および外部クラウドサービスを前提としない。
- 具体的な音声認識技術との連携処理をこの境界に分離する。

Speech Recognition Client の責務は、受け取った audio から transcription text を生成することに限定する。AI Draft の生成、AIService の呼び出し、Target Type / Room / Target の決定、Issue の登録・更新、Repository / SQLAlchemy Session の利用、および audio / transcription text の業務データとしての永続化は行わない。技術固有の失敗は SpeechService でアプリケーション例外へ変換する。

### Invocation

ADR-006 に従い whisper.cpp を使用する。初期実装では Python の `subprocess` から `whisper-cli` を実行する。

初期実装では認識言語として日本語（`-l ja`）を指定する。

`whisper-cli` executable および model のパスはコードへ固定せず、Configuration から取得する。

### Audio Normalization

Speech Transcription API が受け取った audio は、この境界内で whisper.cpp が処理可能な形式へ正規化する。初期実装ではローカルの ffmpeg を Python の `subprocess` から実行し、以下の WAV 形式へ変換してから `whisper-cli` へ渡す。外部クラウドサービスは使用しない。

|項目|形式|
|---|---|
|Sample Rate|16 kHz|
|Channel|Mono|
|Sample Format|PCM 16-bit|

### Temporary Files

入力音声および変換後 WAV は、音声認識処理に必要な temporary file としてのみ保持する。temporary file は成功・失敗にかかわらず処理終了時に削除する。Attachment Storage および SQLite には保存しない。

### Browser Recording

Frontend Voice Input は Browser の `navigator.mediaDevices.getUserMedia({ audio: true })` と `MediaRecorder` を使用して音声を録音する。録音データは `MediaRecorder` が生成する `Blob` として保持し、`FormData` の `audio` field に設定して `POST /api/speech/transcriptions` へ送信する。

Frontend では WAV への変換を行わず、Browser が生成した録音データをそのまま Speech Transcription API へ送信する。Backend の Speech Recognition Client が ffmpeg を使用して 16 kHz / Mono / PCM 16-bit WAV へ正規化する。

文字起こし成功後は response の `text` を既存の Voice / Text Input に反映する。文字起こし結果から AI Draft を自動生成しない。ユーザーが文字起こし結果を確認・修正した後、既存の Generate AI Draft 操作を明示的に実行する。

### Deferred Decisions

whisper.cpp model の種類、`whisper-cli` executable / model file の具体的な配置場所、packaging 方法、MIME Type の正式な許可リスト、最大録音時間、最大ファイルサイズ、および timeout / retry policy は今回決定しない。

Browser が生成する具体的な録音形式は、実行環境の `MediaRecorder` が対応する形式を使用し、特定の MIME Type をアプリケーション側で固定しない。正式な MIME Type の許可リストが必要になった場合は、別途 Detailed Design で決定する。環境変数、concurrency / queue、性能調整も必要に応じて ADR または Detailed Design で決定する。

---

# 8. Domain Models

本章では、システムで利用するドメインモデルを定義する。

ドメインモデルは業務上の概念を表現し、SQLAlchemy Model とは役割を分離する。

初期版では、Repository が SQLAlchemy Model を扱い、Service Layer がドメインルールを適用する。

---

## 8.1 Domain Model Overview

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

## 8.2 Aggregate

本システムでは Issue を Aggregate Root とする。

```text
Issue
 ├── Comment
 └── Attachment
```

Comment および Attachment は必ず Issue に属する。

単独では生成・管理しない。

---

## 8.3 Domain Responsibilities

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

## 8.4 ORM Mapping Policy

SQLAlchemy Model は SQLAlchemy 2.x の型付き ORM を使用する。

Role、Target Type、Category および Status は Python Enum として定義し、DB には Enum の文字列値を保存する。

`relationship` には必要に応じて `back_populates` を使用する。

初期版では、`relationship` に削除 cascade および `delete-orphan` を設定しない。

Foreign Key には `ON DELETE` を指定しない。

Issue の `created_by` と `updated_by` のように同一テーブルを複数回参照する場合は、`relationship` の `foreign_keys` を明示する。

---

## 8.5 Timestamp Policy

Timestamp は UTC で管理する。

アプリケーション内では UTC の timezone-aware datetime を生成する。

SQLite へ保存する際は timezone 情報を除去し、UTC を表す timezone-naive datetime として保存する。

DB から取得した timezone-naive datetime は UTC として扱う。

`created_at`、`updated_at` および `uploaded_at` は Python 側で設定する。

`updated_at` は Service Layer の更新処理で明示的に更新する。

DB の `server_default` および ORM Event による自動更新は使用しない。

---

# 9. DTO Design

本章では、API で利用する DTO (Data Transfer Object) を定義する。

DTO は Pydantic Model として実装する。

---

## 9.1 Authentication DTO

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

## 9.2 Project DTO

### ProjectResponse

```python
id: int
name: str
hotel: dict
```

### ProjectListResponse

```python
projects: list[ProjectResponse]
```

---

## 9.3 Room DTO

### RoomResponse

```python
id: int
room_number: str
display_name: str | None
```

### RoomListResponse

```python
rooms: list[RoomResponse]
```

---

## 9.4 Issue DTO

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

### IssueListResponse

```python
items: list[IssueSummaryResponse]
page: int
page_size: int
total: int
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

## 9.5 AI DTO

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

## 9.6 Comment DTO

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

## 9.7 Attachment DTO

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

## 9.8 DTO Design Policy

DTO 設計では以下の方針を採用する。

- Request DTO と Response DTO を分離する。
- Database Model を API へ直接返却しない。
- API ごとに必要な DTO を定義する。
- 内部実装と API 仕様を分離する。
- DTO には業務ロジックを持たせない。

---

## 9.9 Speech Transcription Schema

### Request

`POST /api/speech/transcriptions` の入力は JSON DTO ではなく、`multipart/form-data` の必須 File フィールド `audio` とする。

API Router は FastAPI の `UploadFile` として受け取り、SpeechService に渡す。audio の必須検証およびエラーの扱いは 12.8 に従う。

### SpeechTranscriptionResponse

`app/schemas/speech.py` に以下の Pydantic Response DTO を定義する。

```python
text: str
```

レスポンスは文字起こし結果の `text` のみとし、Category / Description 等は含めない。

---

# 10. Service Design

本章では、Service Layer の設計を定義する。

Service Layer は業務ロジックを担当し、API RouterとRepository Layer の間に位置する。

---

## 10.1 Service List

|Service|責務|
|---|---|
|AuthService|認証処理|
|AdministrationService|CLI 管理操作の認証・認可、登録・更新、bootstrap および Transaction 管理|
|ProjectService|Project 取得|
|RoomService|Room 一覧取得|
|IssueService|Issue 登録・更新・参照|
|AIService|AI Draft 生成|
|SpeechService|Local Speech Recognition による文字起こしの制御|
|CommentService|Comment 追加・一覧取得|
|AttachmentService|Attachment 追加・一覧取得・ダウンロード・削除|
|StorageService|添付ファイル保存・取得・削除|

---

## 10.2 AuthService

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

## 10.3 ProjectService

### Responsibilities

- Project 一覧取得
- Project 存在確認

### Main Methods

```python
list_projects(user_id: int) -> ProjectListResponse

validate_project_exists(project_id: int) -> None
```

---

## 10.4 RoomService

### Responsibilities

- Hotel 存在確認
- Hotel に属する Room 一覧取得
- Room の DTO 変換

### Main Methods

```python
list_rooms(hotel_id: int) -> RoomListResponse
```

`list_rooms()` は `HotelRepository.find_by_id(hotel_id)` を使用して
指定された Hotel が存在することを確認した後、
`RoomRepository.list_by_hotel(hotel_id)` を使用して Room 一覧を取得する。

取得した Room は `RoomResponse` へ変換し、`RoomListResponse` として返す。

一覧の並び順は `RoomRepository.list_by_hotel()` が返す順序を維持する。

読み取り処理であるため commit は行わない。

---

## 10.5 IssueService

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
) -> IssueListResponse

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

`list_issues()` のページング仕様は以下とする。

|項目|値|
|---|---|
|`page` の既定値|`1`|
|`page_size` の既定値|`20`|
|`page` の最小値|`1`|
|`page_size` の最小値|`1`|
|`page_size` の最大値|`100`|

以下の場合は `ValidationError` とする。

- `page < 1`
- `page_size < 1`
- `page_size > 100`

`list_issues()` は、`page` と `page_size` から `offset` を計算し、`IssueRepository.list_by_project()` で対象ページを取得する。

同一検索条件による総件数は `IssueRepository.count_by_project()` から取得し、`items`、`page`、`page_size` および `total` を持つ `IssueListResponse` を返す。

API Router は Repository を直接呼び出さず、ページング情報を生成しない。

---

## 10.6 AIService

### Responsibilities

- Project 存在確認
- Target Type と Room / Target の整合性検証
- Room 存在確認および Project の Hotel との整合性検証
- 入力テキストの検証
- Ollama Client 呼び出し
- Category および日本語 Description の AI Draft 生成
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

AIService は Issue を保存・更新しない。

入力は Voice / Text Input のテキストとする。Local Speech Recognition による文字起こし結果をユーザーが必要に応じて修正したもの、または直接入力したものを受け取る。raw audio は受け取らず、Local Speech Recognition を呼び出さない。

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

## 10.7 CommentService

### Responsibilities

- Issue 存在確認
- User 存在確認
- Comment 追加
- Comment 一覧取得
- Comment の DTO 変換

### Main Methods

```python
create_comment(
    issue_id: int,
    request: CreateCommentRequest,
    user_id: int
) -> int

list_comments(
    issue_id: int
) -> list[CommentResponse]
```

`create_comment()` は作成した Comment の ID を返却する。

`list_comments()` は Issue の存在を確認した後、`CommentRepository.list_by_issue()` を使用して Comment 一覧を取得する。

取得した Comment は `CommentResponse` へ変換して返す。

Comment 一覧の並び順は `CommentRepository.list_by_issue()` が返す順序を維持する。

`list_comments()` は読み取り処理であり、commit および rollback を行わない。

Comment は編集・削除しない。

---

## 10.8 AttachmentService

### Responsibilities

- Issue 存在確認
- User 存在確認
- Attachment 存在確認
- Attachment と Issue の所属確認
- Attachment 一覧取得
- Attachment の DTO 変換
- ダウンロード対象ファイルの取得
- ファイル名、ファイル形式、ファイルサイズの検証
- StorageService を使用したファイル保存
- Attachment メタデータ登録
- Upload 失敗時のファイル補償削除
- StorageService を使用した Attachment 削除
- DB と Local Storage の整合性制御

### Main Methods

```python
upload_attachment(
    issue_id: int,
    file: UploadFile,
    user_id: int
) -> UploadAttachmentResponse

list_attachments(
    issue_id: int
) -> list[AttachmentResponse]

get_attachment_download(
    attachment_id: int
) -> tuple[Path, str, str]

delete_attachment(
    issue_id: int,
    attachment_id: int,
    user_id: int
) -> None
```

`upload_attachment()` および `delete_attachment()` では User の存在を確認する。

`list_attachments()` は Issue の存在を確認した後、`AttachmentRepository.list_by_issue()` を使用して Attachment 一覧を取得する。

取得した Attachment は `AttachmentResponse` へ変換して返す。

Attachment 一覧の並び順は `AttachmentRepository.list_by_issue()` が返す順序を維持する。

`list_attachments()` は読み取り処理であり、commit および rollback を行わない。

`get_attachment_download()` は `AttachmentRepository.find_by_id()` を使用して Attachment メタデータを取得する。

Attachment メタデータが存在しない場合は `NotFoundError` とする。

Attachment の `file_path` を `StorageService.resolve_file()` へ渡し、Storage Root 配下の安全な物理ファイルパスを取得する。

対応する物理ファイルが存在しない場合は `NotFoundError` とする。

`get_attachment_download()` は以下を順に保持する tuple を返す。

```python
(
    file_path,
    original_file_name,
    mime_type,
)
```

各要素の型と用途は以下とする。

|要素|型|用途|
|---|---|---|
|`file_path`|`Path`|返却する物理ファイル|
|`original_file_name`|`str`|`Content-Disposition` のファイル名|
|`mime_type`|`str`|`Content-Type`|

API Router は返却値を使用してファイルレスポンスを生成する。

ファイルレスポンスの `Content-Disposition` は `inline` とする。

`get_attachment_download()` は読み取り処理であり、commit および rollback を行わない。

`delete_attachment()` の `user_id` は初期版では User 存在確認にのみ使用し、削除者の監査情報や認可判定には使用しない。

AttachmentService は書き込み処理の DB Transaction を管理する。

Repository は commit および rollback を行わない。

---

## 10.9 StorageService

### Responsibilities

- ファイル保存
- ファイル取得
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

resolve_file(
    file_path: str
) -> Path | None

delete_file(
    file_path: str
) -> None
```

`resolve_file()` は、DB に保存された Storage Root からの相対パスを受け取り、Storage Root 配下の安全な物理ファイルパスへ解決する。

以下を確認する。

- `file_path` が絶対パスではないこと。
- `..` 等により Storage Root 外へ逸脱しないこと。
- symlink を経由して Storage Root 外へ逸脱しないこと。
- 解決先が通常ファイルであること。

対象ファイルが存在しない場合は `None` を返す。

Storage Root 外への逸脱、無効なパス、またはファイルシステム処理の失敗は `StorageError` とする。

`resolve_file()` はファイル内容をメモリへ一括読み込みしない。

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

## 10.10 SpeechService

### Responsibilities

- audio が存在することの確認と基本的な入力検証
- Local Speech Recognition boundary の呼び出し
- transcription result の取得
- transcription text が利用可能であることの確認
- Speech Recognition failure の `SpeechRecognitionError` への変換
- transcription text の返却

### Main Methods

```python
transcribe_audio(audio: UploadFile) -> SpeechTranscriptionResponse
```

`transcribe_audio()` は audio を検証してから Local Speech Recognition boundary を呼び出し、取得した text を検証して `SpeechTranscriptionResponse` として返す。Validation は 12.8、例外の HTTP 対応は 13.5 に従う。

SpeechService は以下を行わない。

- AIService の呼び出し
- AI Draft および Category / Description の生成
- Project、Target Type、Room、Target の決定
- Issue の登録・更新
- DB への保存
- audio および transcription text の業務データとしての永続化

SQLAlchemy Session および Repository には依存せず、commit / rollback は行わない。認証は API Layer の既存 Dependency が担当する。

---

## 10.11 AdministrationService / CLI

### Invocation and Commands

Python 標準ライブラリの `argparse` を使用する。`backend/` から以下の形式で実行する。

```bash
uv run python -m app.cli <target> <operation> ...
uv run python -m app.cli user bootstrap-admin --username admin --display-name Administrator
uv run python -m app.cli hotel create --admin-username admin --name "Example Hotel"
uv run python -m app.cli room update 10 --admin-username admin --room-type-id 2
```

通常操作では各 `create` / `update` コマンドに `--admin-username` を必須指定する。更新対象の `id` は位置引数とし、整数で指定する。所属先の ID も整数で指定する。

DB 接続設定と Session の生成には既存 `app/core/config.py` と `app/db/session.py` を利用する。既存 Migration 適用済みの DB を対象とし、CLI が Table 作成や Migration を自動実行することはない。

|Target|Operation|登録時の必須引数|登録時の任意引数 / 更新可能な引数|
|---|---|---|---|
|`hotel`|`create` / `update <id>`|`--name`|更新: `--name`|
|`project`|`create` / `update <id>`|`--hotel-id`, `--name`|更新: `--name`|
|`room-type`|`create` / `update <id>`|`--hotel-id`, `--name`|更新: `--name`|
|`room`|`create` / `update <id>`|`--hotel-id`, `--room-type-id`, `--room-number`|登録: `--display-name`; 更新: `--room-type-id`, `--room-number`, `--display-name`|
|`user`|`create` / `update <id>`|`--username`, `--display-name`, `--role`|更新: `--username`, `--display-name`, `--role`, `--set-password`|
|`user`|`bootstrap-admin`|`--username`, `--display-name`|なし（Role は `ADMINISTRATOR` に固定）|

`--role` は `ADMINISTRATOR` / `ENGINEER` のみ受け付ける。`bootstrap-admin` に `--role` や `--admin-username` は指定しない。Password を渡すコマンドライン引数は提供しない。

更新で省略した項目は維持する。`--role` と `--set-password` の省略時は現在の Role と Password Hash を維持する。更新項目を指定しない場合は成功扱いとし、データおよび Timestamp を変更しない。Room 登録で `--display-name` を省略した場合は null とする。更新時の省略と明示指定を区別し、null へ戻す専用操作は追加しない。

User 登録と bootstrap の Password は非表示入力による必須の入力値とする。`--set-password` は値を取らないフラグとし、指定時だけ新しい Password を入力する。

Project / RoomType / Room の更新に `--hotel-id` は提供せず、所属 Hotel を変更しない。Room の RoomType 変更は同一 Hotel 内に限定する。

CSV、Web 管理画面、Administration Web API、削除操作、DB schema 変更および汎用 CRUD framework は本設計の対象外とする。

### Input and Authentication

CLI は通常操作ごとに、操作する Administrator の Password を `getpass.getpass()` で非表示入力する。User 登録・bootstrap および `--set-password` 指定時は、対象 User の新しい Password を別のプロンプトで非表示入力する。認証用 Password と登録・変更用 Password を区別する。

非表示入力が利用できない場合は、表示入力への fallback を行わず失敗とする。入力中断・EOF は失敗とし、書き込みを行わない。Password の入力は DB Transaction 開始前に完了する。

AdministrationService は同じ SQLAlchemy Session を使用する既存 `AuthService.login()` で毎回認証し、返された Role が `ADMINISTRATOR` であることを検証する。Username 不存在と Password 不一致は共通の `AuthenticationError`、Engineer は `AuthorizationError` とする。CLI は Cookie-based Session を作成・保存しない。

新しい Password は既存 `app/core/security.py` の `hash_password()` でハッシュ化する。独自の長さ・複雑性・確認入力などの Password policy は追加しない。

### Service Methods and DTOs

`app/schemas/administration.py` に管理対象ごとの Create / Update DTO を定義する。型と必須項目は上記の引数および Database Design 6.1～6.5 に合わせる。更新 DTO は項目の指定有無を保持し、省略値を既存 Entity に上書きしない。Password を含む入力 DTO を出力・ログ用データとして使用しない。

名前・username・room_number・display_name・Password は文字列、参照 ID は整数、Role は既存 `Role` Enum とする。Room の display_name のみ null を許可する。更新 DTO は省略を許可するが、指定された NULL 不可項目への null は拒否する。更新で hotel_id など更新対象外の項目を渡した場合も拒否する。

AdministrationService は対象ごとの専用メソッドを持つ。

```text
create_hotel / update_hotel
create_project / update_project
create_room_type / update_room_type
create_room / update_room
create_user / update_user
bootstrap_admin
```

通常メソッドは操作する Administrator の username / password と対象の DTO、更新時は対象 ID を受け取る。`bootstrap_admin` は新規 User の入力だけを受け取る。成功結果は対象の種類、整数 ID および操作結果のみとし、ORM Entity や Password Hash を CLI 出力へ渡さない。

### Validation and Business Rules

必須項目・型・NULL 可否・Role は既存モデルと Database Design に合わせ、DTO と Service Layer で検証する。独自の文字数制限、値の正規化、一意性制約および Password policy は追加しない。ID と Timestamp は利用者に入力させず、Timestamp は8.5に従う。

|対象|Service Layer の検証|
|---|---|
|共通|更新対象が存在すること。存在しない対象は `NotFoundError` とする。|
|Project / RoomType|登録先 Hotel が存在すること。更新では所属 Hotel を維持する。|
|Room|Hotel と RoomType が存在し、RoomType が同一 Hotel に属すること。更新時は変更後の値で検証する。|
|User|username が一意であること。メールアドレス形式も利用可能とする。Role は既存 Enum に従う。|
|Room Number|同一 Hotel 内で room_number が一意であること。別 Hotel では同じ番号を許可する。|

重複検証には既存の `find_by_username()` / `find_by_hotel_and_room_number()` を利用する。更新対象自身と同じ ID の一致は重複扱いにしない。Hotel / Project / RoomType の name に一意性制約は追加しない。Service での重複検証に加え、既存 DB 制約違反も失敗として rollback する。

`bootstrap_admin()` は User が0件の場合だけ許可する。既存 User が1件でもある場合は Role にかかわらず `BusinessRuleError` とし、作成しない。成功時は Role を `ADMINISTRATOR` に固定する。これは空 DB の初期登録であり、既存 User がいて Administrator が0人の場合の復旧機能ではない。

Requirements v1.4 7.14 に従い、User の Role 変更で Administrator を最低1人維持する。現在の Role が `ADMINISTRATOR` で変更後が `ENGINEER` の場合、Administrator 件数が1件なら `BusinessRuleError` とし、2件以上なら変更を許可する。自身の Role 変更にも同じルールを適用する。Role 維持、Engineer から Administrator への変更、Administrator の追加は許可する。

この保護は CLI の引数解析だけで行わず、User 管理の Service Layer に適用する。将来別の入力経路を設ける場合も同じルールを適用する。

### Transaction and Concurrency

1コマンドを1 Transaction とし、AdministrationService が認証・認可、存在確認、業務検証、書き込みおよび commit を同じ SQLAlchemy Session で管理する。成功時に1回 commit、認証・権限・検証・flush・commit 等の失敗時に rollback する。CLI は Session を生成し、処理後に必ず close する。引数解析・入力中断など Transaction 開始前の失敗では DB を変更しない。

User 操作（bootstrap を含む）は最初の DB 読み取り前に SQLite の `BEGIN IMMEDIATE` で書き込み Transaction を開始する。件数確認、認証時の Role 取得、Role 変更および commit を同一 Transaction 内で行い、同時 bootstrap や複数 Administrator の同時降格で制限を破らない。SQLite 固有の開始処理は `app/db/session.py` に置き、AdministrationService が利用する。Repository に認証・件数判定の業務ルールを持たせない。他の管理対象は通常の Transaction を使用する。

書き込みロックを取得できない場合も DB 処理失敗とし、成功扱いにしない。自動再試行やスキーマ変更は追加しない。

### Output and Exit Codes

|終了コード|意味|
|---|---|
|0|成功（`--help` による正常終了も含む）|
|1|認証・権限・入力検証・業務ルール・DB 処理・非表示入力等の失敗|
|2|`argparse` による使用方法エラー（必須引数不足、不明なコマンド / 引数、整数変換失敗、Role の choices 違反等）|

成功は commit 後に stdout へ対象と ID を表示する。失敗は stderr へ利用者向けメッセージを表示する。既存のアプリケーション例外を利用し、CLI の失敗は終了コード1へ変換する。CLI に HTTP status を適用しない。

Password、Password Hash、DB 接続情報、SQL、パラメーターおよび traceback を通常出力しない。DB 例外は安全な共通メッセージへ変換し、認証失敗で username の存在有無を区別しない。ログにも Password / Password Hash を記録しない。

---

# 11. Repository Design

本章では、Repository Layer の設計を定義する。

Repository はデータアクセスのみを担当し、業務ロジックを持たない。

---

## 11.1 Repository List

Hotel の存在確認が必要な処理では、HotelRepository を使用する。

|Repository|責務|
|---|---|
|UserRepository|User 取得・件数取得・登録・更新|
|ProjectRepository|Project 取得（Hotel 情報を含む）・登録・更新|
|HotelRepository|Hotel 取得・登録・更新|
|RoomTypeRepository|RoomType 取得・登録・更新|
|RoomRepository|Room 取得・登録・更新|
|IssueRepository|Issue 取得・登録・更新|
|CommentRepository|Comment 登録・取得|
|AttachmentRepository|Attachment 登録・取得・削除|

---

## 11.2 UserRepository

```python
find_by_id(user_id: int) -> User | None

find_by_username(username: str) -> User | None

count_all() -> int

count_by_role(role: Role) -> int

create(user: User) -> User

update(user: User) -> User
```

---

## 11.3 ProjectRepository

```python
find_by_id(project_id: int) -> Project | None

list_all() -> list[Project]

create(project: Project) -> Project

update(project: Project) -> Project
```

---

## 11.4 HotelRepository

```python
find_by_id(hotel_id: int) -> Hotel | None

create(hotel: Hotel) -> Hotel

update(hotel: Hotel) -> Hotel
```

---

## 11.5 RoomRepository

```python
find_by_id(room_id: int) -> Room | None

find_by_hotel_and_room_number(
    hotel_id: int,
    room_number: str
) -> Room | None

list_by_hotel(hotel_id: int) -> list[Room]

create(room: Room) -> Room

update(room: Room) -> Room
```

初期版では Room 検索機能を提供しないため、Room 名や Room Number による検索メソッドは定義しない。

必要となった場合は追加する。

---

## 11.6 IssueRepository

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

## 11.7 CommentRepository

```python
list_by_issue(issue_id: int) -> list[Comment]

create(comment: Comment) -> Comment
```

---

## 11.8 AttachmentRepository

```python
find_by_id(attachment_id: int) -> Attachment | None

list_by_issue(issue_id: int) -> list[Attachment]

create(attachment: Attachment) -> Attachment

delete(attachment: Attachment) -> None
```

---

## 11.9 RoomTypeRepository / Administration Writes

```python
find_by_id(room_type_id: int) -> RoomType | None

create(room_type: RoomType) -> RoomType

update(room_type: RoomType) -> RoomType
```

既存 Repository の取得処理を再利用し、必要な書き込み操作だけを追加する。各 Repository は同じ SQLAlchemy Session を使用する。`create()` は Entity を add / flush し、`update()` は Service が変更した Entity を flush して返す。commit / rollback は行わない。

User の件数メソッドは DB の件数を返すだけとし、bootstrap の許可や最後の Administrator の判定は AdministrationService が行う。

---

# 12. Validation Design

本章では、Service Layer で実施する Validation を定義する。

---

## 12.1 Common Validation

入力値の型や必須項目の検証は Pydantic により実施する。

Service Layer では、DB の存在確認や業務ルールなど、Pydantic では検証できない内容を検証する。

|対象|Validation|
|---|---|
|ID|対象データが存在すること|
|Required Field|必須項目が入力されていること|
|Enum|定義済み値であること|
|Permission|操作権限があること|

---

## 12.2 Issue Validation

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

## 12.3 Target Type Validation

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

## 12.4 Category Validation

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

## 12.5 Status Validation

Status は以下を許可する。

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

---

## 12.6 Attachment Validation

Attachment 追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_id が存在すること|
|File Type|画像または動画であること|
|File Size|許可されたサイズ以内であること|
|File Name|保存可能なファイル名であること|

---

## 12.7 Comment Validation

Comment 追加時には以下を検証する。

|項目|内容|
|---|---|
|Issue|issue_id が存在すること|
|Comment|空でないこと|

---

## 12.8 Speech Transcription Validation

|対象|Validation|
|---|---|
|audio|必須の File 入力が存在すること|
|transcription text|文字列として取得でき、空ではなく利用可能であること|

SpeechService は audio の基本的な検証を担当し、不正な audio は `ValidationError` とする。multipart の `audio` 欠落など、Service 呼び出し前に検出する入力不正も API Layer で共通エラーレスポンスの `400` として扱う。

Local Speech Recognition の処理失敗、または利用可能な transcription text を取得できない場合は `SpeechRecognitionError` とする。

audio の MIME Type、拡張子、録音時間、ファイルサイズ上限などの具体的な制約は今回決定しない。Attachment の Validation を audio に適用しない。

---

# 13. Error Handling Design

本章では、Backend で利用するエラー処理方針を定義する。

---

## 13.1 Custom Exceptions

以下の共通例外を定義する。

|Exception|用途|
|---|---|
|ValidationError|入力値不正|
|AuthenticationError|認証失敗|
|AuthorizationError|権限不足|
|NotFoundError|対象データなし|
|BusinessRuleError|業務ルール違反|
|AIServiceError|AI 処理失敗|
|SpeechRecognitionError|音声認識処理失敗または利用可能な文字起こし結果を取得できない場合|
|StorageError|ファイル保存・削除失敗|

---

## 13.2 Error Mapping

|Exception|HTTP Status|
|---|---|
|ValidationError|400|
|AuthenticationError|401|
|AuthorizationError|403|
|NotFoundError|404|
|BusinessRuleError|409|
|AIServiceError|500|
|SpeechRecognitionError|500|
|StorageError|500|

---

## 13.3 Error Response

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

## 13.4 Error Message Policy

- ユーザーに理解できるメッセージを返す。
- システム内部情報を返さない。
- 詳細な例外情報はログへ記録する。

---

## 13.5 Speech Transcription Error Handling

|エラー|Application Exception|HTTP Status|
|---|---|---|
|invalid audio|ValidationError|400|
|unauthenticated|AuthenticationError|401|
|speech recognition failure|SpeechRecognitionError|500|

SpeechService は Local Speech Recognition の処理失敗を `SpeechRecognitionError` に変換する。具体的な製品・ライブラリ固有の例外を API へ公開しない。

共通エラーレスポンス形式およびメッセージ方針に従い、音声認識の失敗は AI Draft 生成の失敗と区別する。

---

# 14. Authentication and Authorization Design

本章では、認証および認可の詳細設計を定義する。

---

## 14.1 Authentication Policy

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

## 14.2 Session Configuration

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

## 14.3 User Roles

初期版では以下の Role を定義する。

```text
ADMINISTRATOR
ENGINEER
```

---

## 14.4 Authorization Policy

Role に応じて利用可能な機能を制御する。

|機能|Administrator|Engineer|
|---|---|---|
|Project Selection|Yes|Yes|
|Issue Management|Yes|Yes|
|Speech Transcription|Yes|Yes|
|AI Draft|Yes|Yes|
|Comment Management|Yes|Yes|
|Attachment Management|Yes|Yes|
|Administration|Yes|No|

---

## 14.5 API Dependency

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

## 14.6 Authentication API Session Flow

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

## 14.7 CSRF Policy

初期版では Frontend と Backend を同一 Origin で提供する。

Session Cookie は `SameSite=lax` とする。

初期版では専用の CSRF Token は導入しない。

状態を変更する API は `POST`、`PUT`、`PATCH`、`DELETE` 等の適切な HTTP Method を使用し、GET Request では業務データを変更しない。

CORS で任意の Origin を許可しない。

将来、Frontend と Backend を別 Origin で運用する場合、または外部ネットワークへ公開する場合は、CSRF 対策および Cookie Policy を再検討する。

---

## 14.8 Selected Project Management

選択中の Project はブラウザセッション単位で管理する。

Frontend は選択した Project の識別情報を `sessionStorage` に保存する。

Issue List、Issue Detail、Issue Create および Issue Edit は、`sessionStorage` に保存された Project の識別情報を利用する。

Project が選択されていない場合は、Project Selection 画面へ遷移する。

ログアウト時は `sessionStorage` に保存した Project の識別情報を削除する。

---

## 14.9 Authentication Failure Handling

認証が必要な API で `401 Unauthorized` が返却された場合、Frontend は Login 画面へ遷移する。

Session が無効となった場合も同様とする。

---

# 15. AI Service Design

本章では、AI Draft 生成機能の詳細設計を定義する。

---

## 15.1 AI Service Responsibility

AIService は Ollama を呼び出し、Issue Draft を生成する。

AIService は Voice / Text Input のテキストを解析し、Category および日本語 Description のみを生成する。raw audio を受け取らず、Local Speech Recognition を呼び出さない。

Target Type、Room および Target は生成しない。

AIService は業務データを保存・更新しない。生成結果はユーザーが確認し、必要に応じて修正してから Issue を登録する。

---

## 15.2 AI Draft Input

AI Draft 生成時には以下を入力とする。

|項目|説明|
|---|---|
|project_id|対象 Project|
|target_type|Target Type|
|room_id|ROOM の場合に指定する Room|
|target|OTHER の場合に指定する対象名|
|input_text|Voice / Text Input のテキスト（Local Speech Recognition の文字起こし結果を必要に応じてユーザーが修正したもの、または直接入力したもの）|

---

## 15.3 AI Draft Output

AI Draft は以下を返却する。

|項目|説明|
|---|---|
|category|Category|
|description|日本語の Issue 内容|

---

## 15.4 AI Prompt Policy

Ollama への Prompt は System Message と User Message に分離する。

System Message では以下を明示する。

- CIM の Issue Draft 生成支援であること。
- 出力は Category と Description のみとすること。
- Category は定義済み Category のいずれかとすること。
- Description は入力内容を日本語の自然な Issue 文へ整形すること。
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

## 15.5 AI Error Handling

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

## 15.6 Ollama Integration

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

# 16. File Storage Design

本章では、添付ファイル保存の詳細設計を定義する。

---

## 16.1 Storage Policy

添付ファイル本体は Local Storage へ保存する。

DB には添付ファイルのメタデータのみ保存する。

Speech audio および transcription text は、Issue、Attachment 等の業務データとして永続化しない。Speech audio の保存に Attachment の StorageService や本章の保存方式を流用しない。

Speech audio、transcription および AI Draft 用の Table / Column / Migration は追加しない。ユーザーが確認した AI Draft の内容を既存の Issue 登録処理で保存する流れは維持する。

音声認識処理の temporary file の扱いは 7.7 に従う。

---

## 16.2 Storage Directory

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

## 16.3 File Path Policy

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

## 16.4 File Name Policy

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

## 16.5 File Type Policy

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

## 16.6 File Size Policy

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

## 16.7 File Delete Policy

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

## 16.8 Upload Compensation Policy

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

# 17. Future Enhancements

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
