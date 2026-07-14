# CIM API Design

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-08
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Update authentication specification and login ID policy.|
|1.2|2026-07-08|Align API design with Requirements v1.2. Simplify Target Type to ROOM and OTHER, clarify AI responsibilities, and update Issue APIs.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. API Overview
5. Common API Design
6. Authentication API
7. Project API
8. Issue API
9. AI Draft API
10. Comment API
11. Attachment API
12. Error Response
13. Authorization
14. API Constraints
15. Future Enhancements

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
|Issue|GET|/api/projects/{project_id}/issues|Issue一覧取得|
|Issue|GET|/api/issues/{issue_id}|Issue 詳細取得|
|Issue|POST|/api/projects/{project_id}/issues|Issue 登録|
|Issue|PUT|/api/issues/{issue_id}|Issue更新|
|Issue|PATCH|/api/issues/{issue_id}/status|Status 変更|
|AI|POST|/api/ai/issue-draft|AI Draft生成|
|Comment|POST|/api/issues/{issue_id}/comments|Comment 追加|
|Attachment|POST|/api/issues/{issue_id}/attachments|Attachment 追加|
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

ただし、Attachment Upload は `multipart/form-data` を利用する。

---

## 5.3 DateTime Format

日時は ISO 8601形式で返却する。

```text
2026-06-30T10:30:00
```

---

## 5.4 Authentication

認証が必要な API では、認証済み User のみアクセスできる。

未認証の場合は `401 Unauthorized` を返す。

---

## 5.5 Authorization

権限が不足している場合は `403 Forbidden` を返す。

---

## 5.6 Success Response

成功時は、各APIで定義した JSON レスポンスを返す。

---

## 5.7 Error Response

エラー時は共通エラーレスポンス形式を返す。

詳細は「 12. Error Response 」で定義する。

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

# 8. Issue API

## 8.1 Get Issue List

### Endpoint

```http
GET /api/projects/{project_id}/issues
```

### Description

指定 Project に属する Issue 一覧を取得する。

### Query Parameters

|Parameter|Required|説明|
|---|---|---|
|status|No|Status で絞り込み|
|category|No|Category で絞り込み|
|target_type|No|Target Type で絞り込み|
|keyword|No|Description 検索|
|page|No|ページ番号|
|page_size|No|1ページあたりの件数|

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
|401|未認証|
|404|Projectが存在しない|

---

## 8.2 Get Issue Detail

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

## 8.3 Create Issue

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
  "description": "Bathroom light does not turn off.",
  "raw_input_text": "Bathroom light does not turn off."
}
```

OTHER の例

```json
{
  "room_id": null,
  "target_type": "OTHER",
  "target": "Network",
  "category": "NETWORK",
  "description": "Processor cannot communicate with gateway.",
  "raw_input_text": "Processor cannot communicate with gateway."
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

## 8.4 Update Issue

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

## 8.5 Update Issue Status

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

# 9. AI Draft API

## 9.1 Generate AI Draft

### Endpoint

```http
POST /api/ai/issue-draft
```

### Description

音声入力またはテキスト入力を解析し、Issue Draft を生成する。
AI は業務データを保存せず、生成結果のみを返却する。
AI は Category および Description のみを返却する。
Room、Target Type および Target はレスポンスに含めない。

### Request

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
  "description": "Bathroom light remains on after operation."
}
```

### Error

|Status|内容|
|---|---|
|400|入力値不正|
|401|未認証|
|500|AI 処理失敗|

---

# 10. Comment API

## 10.1 Create Comment

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

## 10.2 Get Comments

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

# 11. Attachment API

## 11.1 Upload Attachment

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
  "file_name": "issue_photo_001.jpg",
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

## 11.2 Get Attachments

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
      "file_name": "issue_photo_001.jpg",
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

## 11.3 Download Attachment

### Endpoint

```http
GET /api/attachments/{attachment_id}
```

### Description

添付ファイルを取得する。

### Response

添付ファイル本体を返却する。

### Error

|Status|内容|
|---|---|
|401|未認証|
|404|Attachment が存在しない|

---

## 11.4 Delete Attachment

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

# 12. Error Response

本章では、APIで共通利用するエラーレスポンス形式を定義する。

---

## 12.1 Error Response Format

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

## 12.2 Error Codes

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

## 12.3 Validation Error Example

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid room_id."
  }
}
```

---

## 12.4 Internal Server Error Example

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Unexpected server error."
  }
}
```

---

# 13. Authorization

本章では API の認可方針を定義する。

---

## 13.1 Roles

システムで利用するロールを以下に示す。

|Role|説明|
|---|---|
|Administrator|システム管理者|
|Engineer|コミッショニング担当者|

---

## 13.2 Authorization Matrix

|API|Administrator|Engineer|
|---|---|---|
|Login|○|○|
|Logout|○|○|
|Current User|○|○|
|Project List|○|○|
|Issue List|○|○|
|Issue Detail|○|○|
|Create Issue|○|○|
|Update Issue|○|○|
|Update Status|○|○|
|AI Draft|○|○|
|Create Comment|○|○|
|Get Comments|○|○|
|Upload Attachment|○|○|
|Get Attachments|○|○|
|Download Attachment|○|○|
|Delete Attachment|○|○|

---

## 13.3 Administration APIs

初期版では、Project 管理・ User 管理・ Master Data 管理は CLI または CSV で実施する。

そのため、Administration 用 Web API は提供しない。

将来的に Web 管理画面を実装する際に、Administration API を追加する。

---

# 14. API Constraints

初期版のAPI設計における制約を以下に示す。

|項目|内容|
|---|---|
|Protocol|HTTP|
|Data Format|JSON (添付ファイルを除く)|
|File Upload|multipart/form-data|
|Authentication|認証必須|
|AI|Ollama|
|Database|SQLite|
|Attachment Storage|Local Storage|
|Issue Delete API|提供しない|
|Comment Update API|提供しない|
|Comment Delete API|提供しない|
|Attachment Update API|提供しない|
|Administration API|提供しない|

---

# 15. Future Enhancements

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
