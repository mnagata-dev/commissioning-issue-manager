# CIM Database Design

**Document Version:** 1.0
**Status:** Draft
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
2. Scope
3. References
4. Database Overview
5. Design Policy
6. Master Data Tables
7. Business Data Tables
8. Constraints
9. Indexes
10. Repository Policy
11. Service Validation Policy
12. Future Enhancements

---

# 1. Purpose

本書は、CIM（Commissioning Issue Manager）のデータベース設計を定義することを目的とする。

本書では、システムで利用するテーブル、リレーション、制約、インデックス、およびデータ管理方針を定義する。

本書を基に、SQLAlchemyモデル、マイグレーション、およびRepository実装を行う。

---

# 2. Scope

本書では以下を対象とする。

* データベース全体構成
* Master Dataテーブル
* Business Dataテーブル
* テーブル間リレーション
* 主キー・外部キー
* 一意制約
* CHECK制約
* インデックス
* Service層で検証する業務ルール

以下は対象外とする。

* API仕様
* DTO設計
* UI設計
* Service実装詳細
* Repository実装詳細
* テストケース

これらは各設計書で定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

| ドキュメント                 | 説明                      |
| ---------------------- | ----------------------- |
| requirements.md        | 要件定義書                   |
| basic_design.md        | 基本設計書                   |
| project_conventions.md | プロジェクト共通ルール             |
| ADR-002                | TargetType Definition   |
| ADR-003                | Category Definition     |
| ADR-004                | Room Model Design       |
| ADR-005                | Issue as Aggregate Root |

---

# 4. Database Overview

初期版ではSQLiteを利用する。

将来的にはPostgreSQLへ移行できる設計とする。

---

## 4.1 Table List

本システムでは以下のテーブルを定義する。

| 分類            | テーブル        | 説明         |
| ------------- | ----------- | ---------- |
| Master Data   | users       | 利用者        |
| Master Data   | hotels      | ホテル        |
| Master Data   | projects    | Project    |
| Master Data   | room_types  | RoomType   |
| Master Data   | rooms       | Room       |
| Business Data | issues      | Issue      |
| Business Data | comments    | Comment    |
| Business Data | attachments | Attachment |

---

## 4.2 Entity Relationship Overview

```text
User
 ├── Issue
 ├── Comment
 └── Attachment

Hotel
 ├── Project
 └── RoomType
      └── Room

Project
 └── Issue
      ├── Comment
      └── Attachment
```

---

## 4.3 Data Classification

本システムのデータは以下に分類する。

### Master Data

システム運用の基礎となる管理データである。

* User
* Hotel
* Project
* RoomType
* Room

### Business Data

コミッショニング業務で日々登録・更新されるデータである。

* Issue
* Comment
* Attachment

---

# 5. Design Policy

## 5.1 Database

初期版ではSQLiteを利用する。

ただし、将来的にPostgreSQLへ移行できるよう、DB依存の実装を最小限に抑える。

---

## 5.2 ID

各テーブルは整数の主キー `id` を持つ。

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
```

---

## 5.3 Timestamp

作成日時・更新日時は以下の方針とする。

| カラム         | 用途           |
| ----------- | ------------ |
| created_at  | 作成日時         |
| updated_at  | 更新日時         |
| uploaded_at | ファイルアップロード日時 |

更新されない履歴データでは、`updated_at` を持たない場合がある。

---

## 5.4 Delete Policy

初期版では、業務上重要なデータの削除は最小限とする。

| データ         | 削除方針        |
| ----------- | ----------- |
| Issue       | 削除しない       |
| Comment     | 削除しない       |
| Attachment  | 削除可能        |
| Master Data | 初期版では画面削除なし |

---

## 5.5 Master Data Management

初期版では、Master DataはCLIまたはCSVで管理する。

Web画面によるMaster Data管理は初期版では実装しない。

---

## 5.6 Business Rule Validation

DB制約だけで表現しにくい業務ルールはService層で検証する。

例：

* 同一Hotel内でRoom Numberが重複しないこと。
* TargetTypeと対象カラムの整合性。
* Issue作成時の必須項目。
* Attachmentのファイル種別・サイズ制限。

---

## 5.7 File Storage

添付ファイル本体はDBには保存しない。

DBにはファイルのメタデータのみ保存する。

ファイル本体はLocal Storageへ保存する。

`file_path` は絶対パスではなく相対パスで保存する。

---

# 6. Master Data Tables

本章では、システムの基礎となるMaster Dataテーブルを定義する。

---

# 6.1 users

システム利用者を管理する。

## Purpose

認証および認可の対象となる利用者情報を保持する。

## Columns

| カラム          | 型        | NULL | 説明                       |
| ------------ | -------- | ---- | ------------------------ |
| id           | INTEGER  | No   | 主キー                      |
| username     | TEXT     | No   | ログイン名                    |
| display_name | TEXT     | No   | 表示名                      |
| role         | TEXT     | No   | Administrator / Engineer |
| created_at   | DATETIME | No   | 作成日時                     |
| updated_at   | DATETIME | No   | 更新日時                     |

## Constraints

* username は一意とする。
* role は定義済みRoleのみ許可する。

---

# 6.2 hotels

Hotelを管理する。

## Purpose

コミッショニング対象となる施設を管理する。

## Columns

| カラム        | 型        | NULL | 説明     |
| ---------- | -------- | ---- | ------ |
| id         | INTEGER  | No   | 主キー    |
| name       | TEXT     | No   | ホテル名   |
| code       | TEXT     | No   | ホテルコード |
| created_at | DATETIME | No   | 作成日時   |
| updated_at | DATETIME | No   | 更新日時   |

## Constraints

* code は一意とする。

---

# 6.3 projects

Projectを管理する。

## Purpose

コミッショニング案件を管理する。

## Columns

| カラム        | 型        | NULL | 説明         |
| ---------- | -------- | ---- | ---------- |
| id         | INTEGER  | No   | 主キー        |
| hotel_id   | INTEGER  | No   | Hotel      |
| name       | TEXT     | No   | Project名   |
| code       | TEXT     | No   | Projectコード |
| created_at | DATETIME | No   | 作成日時       |
| updated_at | DATETIME | No   | 更新日時       |

## Foreign Keys

| カラム      | 参照先       |
| -------- | --------- |
| hotel_id | hotels.id |

## Constraints

* hotel_id は必須とする。
* code は一意とする。

---

# 6.4 room_types

RoomTypeを管理する。

## Purpose

Roomの種別を管理する。

## Columns

| カラム         | 型        | NULL | 説明          |
| ----------- | -------- | ---- | ----------- |
| id          | INTEGER  | No   | 主キー         |
| hotel_id    | INTEGER  | No   | Hotel       |
| name        | TEXT     | No   | RoomType名   |
| code        | TEXT     | No   | RoomTypeコード |
| description | TEXT     | Yes  | 説明          |
| created_at  | DATETIME | No   | 作成日時        |
| updated_at  | DATETIME | No   | 更新日時        |

## Foreign Keys

| カラム      | 参照先       |
| -------- | --------- |
| hotel_id | hotels.id |

## Constraints

* 同一Hotel内でcodeは一意とする。

---

# 6.5 rooms

Roomを管理する。

## Purpose

Project内で管理する部屋情報を保持する。

## Columns

| カラム          | 型        | NULL | 説明       |
| ------------ | -------- | ---- | -------- |
| id           | INTEGER  | No   | 主キー      |
| project_id   | INTEGER  | No   | Project  |
| room_type_id | INTEGER  | No   | RoomType |
| room_number  | TEXT     | No   | 部屋番号     |
| display_name | TEXT     | Yes  | 表示名      |
| floor        | TEXT     | Yes  | フロア      |
| created_at   | DATETIME | No   | 作成日時     |
| updated_at   | DATETIME | No   | 更新日時     |

## Foreign Keys

| カラム          | 参照先           |
| ------------ | ------------- |
| project_id   | projects.id   |
| room_type_id | room_types.id |

## Constraints

* room_number は必須とする。
* room_type_id は必須とする。

同一Project内では room_number を一意とする。

---

# 6.6 Master Data Relationships

Master Data間のリレーションを以下に示す。

```text
Hotel
 │
 ├── Project
 │
 └── RoomType
        │
        ▼
      Room
```

---

## 6.7 Relationship Summary

| 親テーブル      | 子テーブル      | 関係    |
| ---------- | ---------- | ----- |
| hotels     | projects   | 1 : N |
| hotels     | room_types | 1 : N |
| projects   | rooms      | 1 : N |
| room_types | rooms      | 1 : N |

---

## 6.8 Management Policy

初期版では以下のMaster DataをCLIまたはCSVで管理する。

* User
* Hotel
* Project
* RoomType
* Room

Web画面による管理機能は提供しない。

---

# 7. Business Data Tables

本章では、コミッショニング業務で利用するBusiness Dataテーブルを定義する。

Issueを集約ルート（Aggregate Root）とし、CommentおよびAttachmentはIssueに従属する。

---

# 7.1 issues

Issueを管理する。

## Purpose

コミッショニング時に発生した課題、確認事項および改善項目を管理する。

## Columns

| カラム         | 型        | NULL | 説明         |
| ----------- | -------- | ---- | ---------- |
| id          | INTEGER  | No   | 主キー        |
| project_id  | INTEGER  | No   | Project    |
| room_id     | INTEGER  | No   | Room       |
| target_type | TEXT     | No   | TargetType |
| target      | TEXT     | No   | 対象機器・対象箇所  |
| category    | TEXT     | No   | Category   |
| description | TEXT     | No   | 詳細説明       |
| status      | TEXT     | No   | Issue状態    |
| created_by  | INTEGER  | No   | 登録者        |
| created_at  | DATETIME | No   | 作成日時       |
| updated_at  | DATETIME | No   | 更新日時       |

## Foreign Keys

| カラム        | 参照先         |
| ---------- | ----------- |
| project_id | projects.id |
| room_id    | rooms.id    |
| created_by | users.id    |

## Constraints

* project_idは必須とする。
* room_idは必須とする。
* descriptionは必須とする。
* target_typeは定義済みTargetTypeのみ許可する。
* categoryは定義済みCategoryのみ許可する。
* statusは定義済みStatusのみ許可する。

---

# 7.2 comments

Commentを管理する。

## Purpose

Issueに対するコメント履歴を保持する。

## Columns

| カラム        | 型        | NULL | 説明    |
| ---------- | -------- | ---- | ----- |
| id         | INTEGER  | No   | 主キー   |
| issue_id   | INTEGER  | No   | Issue |
| comment    | TEXT     | No   | コメント  |
| created_by | INTEGER  | No   | 登録者   |
| created_at | DATETIME | No   | 作成日時  |

## Foreign Keys

| カラム        | 参照先       |
| ---------- | --------- |
| issue_id   | issues.id |
| created_by | users.id  |

## Constraints

* issue_idは必須とする。
* commentは必須とする。

Commentは履歴データであるため、更新日時（updated_at）は保持しない。

---

# 7.3 attachments

Attachmentを管理する。

## Purpose

Issueへ添付した写真・動画を管理する。

## Columns

| カラム                | 型        | NULL | 説明            |
| ------------------ | -------- | ---- | ------------- |
| id                 | INTEGER  | No   | 主キー           |
| issue_id           | INTEGER  | No   | Issue         |
| file_name          | TEXT     | No   | 保存ファイル名       |
| original_file_name | TEXT     | No   | 元ファイル名        |
| file_path          | TEXT     | No   | 相対保存パス        |
| mime_type          | TEXT     | No   | MIME Type     |
| file_size          | INTEGER  | No   | ファイルサイズ（Byte） |
| uploaded_by        | INTEGER  | No   | 登録者           |
| uploaded_at        | DATETIME | No   | アップロード日時      |

## Foreign Keys

| カラム         | 参照先       |
| ----------- | --------- |
| issue_id    | issues.id |
| uploaded_by | users.id  |

## Constraints

* issue_idは必須とする。
* file_nameは必須とする。
* file_pathは必須とする。
* file_sizeは0より大きい値とする。

添付ファイル本体はLocal Storageに保存し、本テーブルではメタデータのみ管理する。

---

# 7.4 Business Data Relationships

Business Data間のリレーションを以下に示す。

```text
Project
    │
    ▼
 Issue
 ├──────┐
 ▼      ▼
Comment Attachment
```

---

## 7.5 Relationship Summary

| 親テーブル    | 子テーブル       | 関係    |
| -------- | ----------- | ----- |
| projects | issues      | 1 : N |
| rooms    | issues      | 1 : N |
| users    | issues      | 1 : N |
| issues   | comments    | 1 : N |
| users    | comments    | 1 : N |
| issues   | attachments | 1 : N |
| users    | attachments | 1 : N |

---

## 7.6 Aggregate Design

IssueをAggregate Rootとする。

CommentおよびAttachmentは単独では存在できず、必ずIssueに属する。

Issueを削除しない運用とするため、CommentおよびAttachmentも業務データとして保持される。

Business Dataの整合性はIssueを中心として維持する。

---

# 8. Constraints

本章では、データベース設計における制約を定義する。

---

## 8.1 Primary Keys

すべてのテーブルは単一の主キー `id` を持つ。

| テーブル        | 主キー |
| ----------- | --- |
| users       | id  |
| hotels      | id  |
| projects    | id  |
| room_types  | id  |
| rooms       | id  |
| issues      | id  |
| comments    | id  |
| attachments | id  |

---

## 8.2 Foreign Keys

各テーブルの外部キーを以下に示す。

| テーブル        | 外部キー         | 参照先           |
| ----------- | ------------ | ------------- |
| projects    | hotel_id     | hotels.id     |
| room_types  | hotel_id     | hotels.id     |
| rooms       | project_id   | projects.id   |
| rooms       | room_type_id | room_types.id |
| issues      | project_id   | projects.id   |
| issues      | room_id      | rooms.id      |
| issues      | created_by   | users.id      |
| comments    | issue_id     | issues.id     |
| comments    | created_by   | users.id      |
| attachments | issue_id     | issues.id     |
| attachments | uploaded_by  | users.id      |

---

## 8.3 Unique Constraints

| テーブル       | 制約                        |
| ---------- | ------------------------- |
| users      | username                  |
| hotels     | code                      |
| projects   | code                      |
| room_types | (hotel_id, code)          |
| rooms      | (project_id, room_number) |

---

## 8.4 Delete Policy

初期版では、業務データの削除は最小限とする。

| テーブル        | 削除方針           |
| ----------- | -------------- |
| users       | CLIまたはCSVによる管理 |
| hotels      | CLIまたはCSVによる管理 |
| projects    | CLIまたはCSVによる管理 |
| room_types  | CLIまたはCSVによる管理 |
| rooms       | CLIまたはCSVによる管理 |
| issues      | 削除しない          |
| comments    | 削除しない          |
| attachments | 削除可能           |

---

# 9. Indexes

検索性能向上のため、以下のインデックスを作成する。

| テーブル        | カラム        | 用途                 |
| ----------- | ---------- | ------------------ |
| projects    | hotel_id   | Hotel検索            |
| room_types  | hotel_id   | RoomType検索         |
| rooms       | project_id | Project内Room検索     |
| issues      | project_id | Project内Issue検索    |
| issues      | room_id    | Room別Issue検索       |
| issues      | status     | Status検索           |
| issues      | category   | Category検索         |
| comments    | issue_id   | Issue別Comment検索    |
| attachments | issue_id   | Issue別Attachment検索 |

---

# 10. Repository Policy

Repositoryはデータアクセスのみを担当する。

## Responsibilities

Repositoryは以下を担当する。

* データ取得
* データ登録
* データ更新
* データ削除
* 検索

Repositoryでは業務ロジックを実装しない。

---

## Repository Structure

各AggregateごとにRepositoryを定義する。

```text id="m31w9v"
UserRepository

ProjectRepository

RoomRepository

IssueRepository
```

CommentおよびAttachmentはIssue Aggregateに属するため、必要に応じて専用Repositoryを設ける。

---

# 11. Service Validation Policy

業務ルールはService Layerで検証する。

## Validation Examples

Service Layerでは以下を検証する。

* 必須項目
* TargetType
* Category
* Status
* Room存在確認
* Project存在確認
* User存在確認
* Attachmentのサイズ
* Attachmentの拡張子
* 業務ルール

DB制約では表現できないルールはService Layerで実装する。

---

# 12. Future Enhancements

将来的な拡張を以下に示す。

* PostgreSQLへの移行
* Full Text Search対応
* 添付ファイル保存先の変更（NAS・クラウドストレージ）
* Audit Logテーブル追加
* Notificationテーブル追加
* AI実行履歴テーブル追加
* Soft Delete対応
* 履歴管理テーブル追加

これらは初期版の設計範囲には含めない。

---

# End of Document
