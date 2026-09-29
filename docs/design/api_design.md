# CIM API Design

- **Document Version:** 1.3
- **Status:** Draft
- **Last Updated:** 2026-09-29
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Update authentication specification and login ID policy.|
|1.2|2026-07-08|Align API design with Requirements v1.2. Simplify Target Type to ROOM and OTHER, clarify AI responsibilities, and update Issue APIs.|
|1.3|2026-09-29|Align API design with Requirements v1.3 and Basic Design v1.3 for offline operation, local voice transcription, and Japanese Description generation.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. API Overview
5. Common API Design
6. Authentication API
7. Project API
8. Room API
9. Issue API
10. Speech Transcription API
11. AI Draft API
12. Comment API
13. Attachment API
14. Error Response
15. Authorization
16. API Constraints
17. Future Enhancements

---

# 1. Purpose

本書は、CIM (Commissioning Issue Manager) の API 設計を定義することを目的とする。

本書では、Frontend と Backend 間で利用する REST API のエンドポイント、リクエスト、レスポンス、およびエラー仕様を定義する。

---

# 2. Scope

本書では以下を対象とする。

- REST API一覧
- HTTP Method
- Endpoint
- Request
- Response
- Error Response
- 認証・認可方針

以下は対象外とする。

- DB テーブル定義
- Service 実装
- Repository 実装
- UI 詳細設計
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
|project_conventions.md|プロジェクト共通ルール|
|ADR-001|User in Control|
|ADR-002|TargetType Definition|
|ADR-003|Category Definition|
|ADR-005|Issue as Aggregate Root|

---

# 4. API Overview

初期版では以下のAPIを提供する。

|分類|Method|Endpoint|概要|
|---|---|---|---|
|Authentication|POST|/api/auth/login|ログイン|
|Authentication|POST|/api/auth/logout|ログアウト|
|Authentication|GET|/api/auth/me|ログイン中ユーザー取得|
|Project|GET|/api/projects|Project一覧取得|
|Room|GET|/api/hotels/{hotel_id}/rooms|Room一覧取得|
|Issue|GET|/api/projects/{project_id}/issues|Issue一覧取得|
|Issue|GET|/api/issues/{issue_id}|Issue 詳細取得|
|Issue|POST|/api/projects/{project_id}/issues|Issue 登録|
|Issue|PUT|/api/issues/{issue_id}|Issue更新|
|Issue|PATCH|/api/issues/{issue_id}/status|Status 変更|
|Speech|POST|/api/speech/transcriptions|音声をローカルで文字起こしする。|
|AI|POST|/api/ai/issue-draft|AI Draft生成|
|Comment|POST|/api/issues/{issue_id}/comments|Comment 追加|
|Attachment|POST|/api/issues/{issue_id}/attachments|Attachment 追加|
|Attachment|GET|/api/issues/{issue_id}/attachments|Attachment 一覧取得|
|Attachment|GET|/api/attachments/{attachment_id}|Attachment ダウンロード|
|Attachment|DELETE|/api/issues/{issue_id}/attachments/{attachment_id}|Attachment 削除|

---

# 5. Common API Design

## 5.1 Base URL

すべての API は以下の Prefix を持つ。

```text
/api
```

---

## 5.2 Format

リクエストおよびレスポンスは原則として JSON 形式とする。

ただし、Attachment Upload および Speech Transcription のリクエストは `multipart/form-data` を利用する。

---

## 5.3 DateTime Format

日時は ISO 8601形式で返却する。

```text
2026-06-30T10:30:00
```

---

## 5.4 Authentication

認証には Cookie-based Session を使用する。

ログイン成功時、Session に認証済み User の `id` を `user_id` として保存する。

認証が必要な API では、Session に保存された `user_id` を基に認証済み User を取得する。

Session が存在しない場合、Session に `user_id` が存在しない場合、または `user_id` に対応する User が存在しない場合は `401 Unauthorized` を返す。

---

## 5.5 Authorization

権限が不足している場合は `403 Forbidden` を返す。

---

## 5.6 Success Response

成功時は、各APIで定義した JSON レスポンスを返す。

---

## 5.7 Error Response

エラー時は共通エラーレスポンス形式を返す。

詳細は「 14. Error Response 」で定義する。

---

# 6. Authentication API

## 6.1 Login

### Endpoint

```http
POST /api/auth/login
```

### Description

ユーザーがログインする。

username はログイン ID とし、メールアドレス形式も利用できる。

認証成功時、Session に認証済み User の `id` を `user_id` として保存する。

認証失敗時は Session を作成せず、`401 Unauthorized` を返す。

### Request

```json
{
  "username": "engineer1@example.com",
  "password": "password"
}
```

### Response

```json
{
  "user": {
    "id": 1,
    "username": "engineer1@example.com",
    "display_name": "Engineer 1",
    "role": "ENGINEER"
  }
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|認証失敗|

---

## 6.2 Logout

### Endpoint

```http
POST /api/auth/logout
```

### Description

ユーザーがログアウトする。

認証済みであることを確認した後、Session を削除する。

ログアウト成功後、それまで使用していた Session では認証が必要な API を利用できない。

### Response

```json
{
  "message": "Logged out"
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|

---

## 6.3 Current User

### Endpoint

```http
GET /api/auth/me
```

### Description

ログイン中のユーザー情報を取得する。

Session に保存された `user_id` を基に現在の User 情報を取得する。

Session が存在しない場合、Session に `user_id` が存在しない場合、または `user_id` に対応する User が存在しない場合は `401 Unauthorized` を返す。

### Response

```json
{
  "id": 1,
  "username": "engineer1@example.com",
  "display_name": "Engineer 1",
  "role": "ENGINEER"
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|

---

# 7. Project API

## 7.1 Get Projects

### Endpoint

```http
GET /api/projects
```

### Description

Engineer が選択可能な Project 一覧を取得する。

### Response

```json
{
  "projects": [
    {
      "id": 1,
      "name": "Hotel A Commissioning",
      "hotel": {
        "id": 1,
        "name": "Hotel A"
      }
    }
  ]
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|

---

# 8. Room API

## 8.1 Get Rooms

### Endpoint

```http
GET /api/hotels/{hotel_id}/rooms
```

### Description

指定 Hotel に属する Room 一覧を取得する。

Issue Create および Issue Edit で Target Type = ROOM の場合の Room 選択に利用する。

### Response

```json
{
  "rooms": [
    {
      "id": 1,
      "room_number": "1203",
      "display_name": null
    }
  ]
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Hotel が存在しない|

---

# 9. Issue API

## 9.1 Get Issue List

### Endpoint

```http
GET /api/projects/{project_id}/issues
```

### Description

指定 Project に属する Issue 一覧を取得する。

Issue 一覧は updated_at の降順（新しく更新された Issue を先頭）で返却する。

### Query Parameters

|Parameter|Required|Default|Validation|説明|
|---|---|---|---|---|
|status|No|-|定義済み Status|Status で絞り込み|
|category|No|-|定義済み Category|Category で絞り込み|
|target_type|No|-|`ROOM` または `OTHER`|Target Type で絞り込み|
|keyword|No|-|-|Description 検索|
|page|No|`1`|1以上|ページ番号|
|page_size|No|`20`|1以上100以下|1ページあたりの件数|

### Response

```json
{
  "items": [
    {
      "id": 101,
      "room": {
        "id": 1,
        "room_number": "1203"
      },
      "target_type": "ROOM",
      "target": null,
      "category": "LIGHTING",
      "description": "Bathroom light does not turn off.",
      "status": "OPEN",
      "updated_at": "2026-06-30T10:30:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

### Error

|Status|内容|
|---|---|
|400|Query Parameter が不正|
|401|未認証|
|404|Project が存在しない|

---

## 9.2 Get Issue Detail

### Endpoint

```http
GET /api/issues/{issue_id}
```

### Description

Issue 詳細を取得する。

Comment および Attachment 一覧も含めて返却する。

### Response

```json
{
  "id": 101,
  "project": {
    "id": 1,
    "name": "Hotel A Commissioning"
  },
  "room": {
    "id": 1,
    "room_number": "1203"
  },
  "target_type": "ROOM",
  "target": null,
  "category": "LIGHTING",
  "description": "Bathroom light does not turn off.",
  "status": "OPEN",
  "created_by": {
    "id": 1,
    "display_name": "Engineer 1"
  },
  "updated_by": {
    "id": 2,
    "display_name": "Engineer 2"
  },
  "created_at": "2026-06-30T10:00:00",
  "updated_at": "2026-06-30T10:30:00",
  "comments": [
    {
      "id": 1,
      "comment": "Checked on site.",
      "created_by": {
        "id": 1,
        "display_name": "Engineer 1"
      },
      "created_at": "2026-06-30T10:20:00"
    }
  ],
  "attachments": [
    {
      "id": 1,
      "file_name": "photo1.jpg",
      "mime_type": "image/jpeg",
      "file_size": 204800,
      "uploaded_at": "2026-06-30T10:25:00"
    }
  ]
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Issueが存在しない|

---

## 9.3 Create Issue

### Endpoint

```http
POST /api/projects/{project_id}/issues
```

### Description

指定 Project に Issue を登録する。

### Request

Target Type が ROOM の場合は、room_id を指定する。

Target Type が OTHER の場合は、room_id を null とし、target に対象名を指定する。

ROOM の例

```json
{
  "room_id": 1,
  "target_type": "ROOM",
  "category": "LIGHTING",
  "description": "Bathroom light does not turn off."
}
```

OTHER の例

```json
{
  "room_id": null,
  "target_type": "OTHER",
  "target": "Network",
  "category": "NETWORK",
  "description": "Processor cannot communicate with gateway."
}
```

### Response

```json
{
  "id": 101,
  "message": "Issue created"
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|404|Project が存在しない|

---

## 9.4 Update Issue

### Endpoint

```http
PUT /api/issues/{issue_id}
```

### Description

Issue 内容を更新する。

### Request

Target Type が ROOM の場合は、room_id を指定する。

Target Type が OTHER の場合は、room_id を null とし、target に対象名を指定する。

ROOM の例

```json
{
  "room_id": 1,
  "target_type": "ROOM",
  "category": "LIGHTING",
  "description": "Bathroom light remains on after Master OFF."
}
```

OTHER の例

```json
{
  "room_id": null,
  "target_type": "OTHER",
  "target": "Network",
  "category": "NETWORK",
  "description": "Processor cannot communicate with gateway."
}
```

### Response

```json
{
  "id": 101,
  "message": "Issue updated"
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|404|Issueが存在しない|

---

## 9.5 Update Issue Status

### Endpoint

```http
PATCH /api/issues/{issue_id}/status
```

### Description

Issue の Status を変更する。

### Request

```json
{
  "status": "IN_PROGRESS"
}
```

### Allowed Status

以下の Status を指定できる。

- OPEN
- IN_PROGRESS
- RESOLVED
- CLOSED

### Response

```json
{
  "id": 101,
  "status": "IN_PROGRESS",
  "message": "Status updated"
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|404|Issue が存在しない|

---

# 10. Speech Transcription API

## 10.1 Transcribe Speech

### Endpoint

```http
POST /api/speech/transcriptions
```

### Description

Frontend から受け取った音声を Local Speech Recognition で文字起こしし、結果のテキストのみを返却する。

音声認識処理はローカル環境で完結し、外部クラウドサービスを必要としない。

音声データおよび文字起こし結果を業務データとして保存しない。
Category および Description の生成、Issue の登録・更新は行わない。

返却された文字起こし結果は Frontend の既存の Voice / Text Input に表示され、ユーザーが必要に応じて修正した後、AI Draft 生成に利用する。
文字起こし結果の確認または修正は、独立した必須操作としない。

### Request

Content-Type:

```text
multipart/form-data
```

### Form Data

|Name|型|必須|説明|
|---|---|:-:|---|
|audio|File|Yes|文字起こし対象の音声|

### Response

```json
{
  "text": "ロビーの照明が点滅している"
}
```

### Error

|Status|内容|
|---|---|
|400|入力音声不正|
|401|未認証|
|500|音声認識処理失敗|

---

# 11. AI Draft API

## 11.1 Generate AI Draft

### Endpoint

```http
POST /api/ai/issue-draft
```

### Description

Voice / Text Input に入力されたテキストを解析し、Issue Draft を生成する。
AI は業務データを保存せず、生成結果のみを返却する。
AI は Category および Description のみを生成して返却し、Description は日本語とする。
Room、Target Type および Target はレスポンスに含めない。

生成結果は入力支援のための Draft とし、ユーザーが内容を確認し、必要に応じて修正した後に Issue を登録する（User in Control）。

### Request

input_text は、Local Speech Recognition による文字起こし結果（必要に応じてユーザーが修正したテキスト）、またはユーザーが直接入力したテキストを表す。

AI は Target Type、Room および Target を決定しない。

Target Type、Room および Target は、AI Draft 生成前にユーザーが指定する。

ROOM の例

```json
{
  "project_id": 1,
  "target_type": "ROOM",
  "room_id": 1,
  "target": null,
  "input_text": "Bathroom light does not turn off."
}
```

OTHER の例

```json
{
  "project_id": 1,
  "target_type": "OTHER",
  "room_id": null,
  "target": "Network",
  "input_text": "Processor cannot communicate with gateway."
}
```

### Response

```json
{
  "category": "LIGHTING",
  "description": "バスルームのダウンライトが操作後も消灯しない。"
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|404|Project または Room が存在しない|
|500|AI 処理失敗|

---

# 12. Comment API

## 12.1 Create Comment

### Endpoint

```http
POST /api/issues/{issue_id}/comments
```

### Description

Issue へ Comment を追加する。

### Request

```json
{
  "comment": "Checked on site. Reproduced successfully."
}
```

### Response

```json
{
  "id": 1,
  "message": "Comment created"
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|404|Issueが存在しない|

---

## 12.2 Get Comments

### Endpoint

```http
GET /api/issues/{issue_id}/comments
```

### Description

Issue に登録されている Comment 一覧を取得する。

### Response

```json
{
  "items": [
    {
      "id": 1,
      "comment": "Checked on site.",
      "created_by": {
        "id": 1,
        "display_name": "Engineer 1"
      },
      "created_at": "2026-06-30T10:20:00"
    }
  ]
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Issue が存在しない|

---

# 13. Attachment API

## 13.1 Upload Attachment

### Endpoint

```http
POST /api/issues/{issue_id}/attachments
```

### Description

Issue へ添付ファイルを追加する。

### Request

Content-Type:

```text
multipart/form-data
```

### Form Data

|Name|型|必須|説明|
|---|---|:-:|---|
|file|File|Yes|添付ファイル|

### Response

```json
{
  "id": 1,
  "file_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "message": "Attachment uploaded"
}
```

### Error

|Status|内容|
|---|---|
|400|ファイル不正|
|401|未認証|
|404|Issueが存在しない|

---

## 13.2 Get Attachments

### Endpoint

```http
GET /api/issues/{issue_id}/attachments
```

### Description

Issue に添付されている Attachment 一覧を取得する。

### Response

```json
{
  "items": [
    {
      "id": 1,
      "file_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
      "mime_type": "image/jpeg",
      "file_size": 204800,
      "uploaded_at": "2026-06-30T10:25:00"
    }
  ]
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Issue が存在しない|

---

## 13.3 Download Attachment

### Endpoint

```http
GET /api/attachments/{attachment_id}
```

### Description

指定された Attachment のファイル本体を返却する。

Attachment メタデータが存在しない場合、または対応する物理ファイルが Local Storage に存在しない場合は `404 Not Found` を返す。

### Response Headers

|Header|値|
|---|---|
|`Content-Type`|Attachment メタデータの `mime_type`|
|`Content-Disposition`|`inline`|
|Filename|Attachment メタデータの `original_file_name`|

`Content-Disposition` のファイル名には、Local Storage 上の保存名である `file_name` ではなく、アップロード時の元ファイル名である `original_file_name` を使用する。

ファイル名を含む `Content-Disposition` Header は、Starlette の `FileResponse` 等を利用して安全に生成する。Header文字列を手動で組み立てない。

### Response Body

Attachment の物理ファイル本体を返却する。

画像および動画は、ブラウザで表示可能な場合にインライン表示できるレスポンスとする。

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Attachment または物理ファイルが存在しない|
|500|ファイル取得処理に失敗|

---

## 13.4 Delete Attachment

### Endpoint

```http
DELETE /api/issues/{issue_id}/attachments/{attachment_id}
```

### Description

Issue から Attachment を削除する。

添付ファイル本体および管理情報を削除する。

### Response

```json
{
  "message": "Attachment deleted"
}
```

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Issue または Attachment が存在しない|

---

# 14. Error Response

本章では、APIで共通利用するエラーレスポンス形式を定義する。

---

## 14.1 Error Response Format

エラー時は以下の JSON 形式で返却する。

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed."
  }
}
```

---

## 14.2 Error Codes

|Code|HTTP Status|説明|
|---|---|---|
|VALIDATION_ERROR|400|入力値が不正|
|UNAUTHORIZED|401|認証されていない|
|FORBIDDEN|403|権限不足|
|NOT_FOUND|404|リソースが存在しない|
|CONFLICT|409|データ競合|
|INTERNAL_SERVER_ERROR|500|システム内部エラー|
|AI_SERVICE_ERROR|500|AIサービス実行エラー|

---

## 14.3 Validation Error Example

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid room_id."
  }
}
```

---

## 14.4 Internal Server Error Example

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Unexpected server error."
  }
}
```

---

# 15. Authorization

本章では API の認可方針を定義する。

---

## 15.1 Roles

システムで利用するロールを以下に示す。

|Role|説明|
|---|---|
|Administrator|システム管理者|
|Engineer|コミッショニング担当者|

---

## 15.2 Authorization Matrix

|API|Administrator|Engineer|
|---|---|---|
|Login|○|○|
|Logout|○|○|
|Current User|○|○|
|Project List|○|○|
|Room List|○|○|
|Issue List|○|○|
|Issue Detail|○|○|
|Create Issue|○|○|
|Update Issue|○|○|
|Update Status|○|○|
|Speech Transcription|○|○|
|AI Draft|○|○|
|Create Comment|○|○|
|Get Comments|○|○|
|Upload Attachment|○|○|
|Get Attachments|○|○|
|Download Attachment|○|○|
|Delete Attachment|○|○|

---

## 15.3 Administration APIs

初期版では、Project 管理・ User 管理・ Master Data 管理は CLI または CSV で実施する。

そのため、Administration 用 Web API は提供しない。

将来的に Web 管理画面を実装する際に、Administration API を追加する。

---

# 16. API Constraints

初期版のAPI設計における制約を以下に示す。

|項目|内容|
|---|---|
|Protocol|HTTP|
|Data Format|JSON (添付ファイルおよび Speech Transcription のリクエストを除く)|
|File Upload|multipart/form-data|
|Authentication|認証必須|
|AI|Ollama|
|Offline Operation|初期版の Speech Transcription および AI Draft は、必要なモデルと実行環境をローカルで利用可能とし、インターネット接続および外部クラウドサービスを前提としない。|
|Database|SQLite|
|Attachment Storage|Local Storage|
|Issue Delete API|提供しない|
|Comment Update API|提供しない|
|Comment Delete API|提供しない|
|Attachment Update API|提供しない|
|Administration API|提供しない|

---

# 17. Future Enhancements

将来的なAPI拡張を以下に示す。

- Administration API
- User Management API
- Project Management API
- Master Data API
- Issue Search API の検索条件拡張
- Issue 履歴取得 API
- Notification API
- Audit Log API
- AI 設定 API
- WebSocket によるリアルタイム更新
- API バージョニング

これらは初期版の設計範囲には含めない。

---

# End of Document
