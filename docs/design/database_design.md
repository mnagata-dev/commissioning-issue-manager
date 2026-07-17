# CIM Database Design

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-09
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Remove code columns, remove RoomType.description and add password_hash to User.|
|1.2|2026-07-09|Align database design with Requirements v1.2. Simplify Target Type to ROOM and OTHER, remove floor from Room, and clarify Issue target relationships.|

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

本書は、CIM(Commissioning Issue Manager)のデータベース設計を定義することを目的とする。

本書では、システムで利用するテーブル、リレーション、制約、インデックス、およびデータ管理方針を定義する。

本書を基に、SQLAlchemy モデル、マイグレーション、および Repository 実装を行う。

---

# 2. Scope

本書では以下を対象とする。

- データベース全体構成
- Master Data テーブル
- Business Data テーブル
- テーブル間リレーション
- 主キー・外部キー
- 一意制約
- CHECK 制約
- インデックス
- Service 層で検証する業務ルール

以下は対象外とする。

- API 仕様
- DTO 設計
- UI 設計
- Service 実装詳細
- Repository 実装詳細
- テストケース

これらは各設計書で定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

|ドキュメント|説明|
|---|---|
|requirements.md|要件定義書|
|basic_design.md|基本設計書|
|project_conventions.md|プロジェクト共通ルール|
|ADR-002|TargetType Definition|
|ADR-003|Category Definition|
|ADR-004|Room Model Design|
|ADR-005|Issue as Aggregate Root|

---

# 4. Database Overview

初期版では SQLite を利用する。

将来的には PostgreSQL へ移行できる設計とする。

---

## 4.1 Table List

本システムでは以下のテーブルを定義する。

|分類|テーブル|説明|
|---|---|---|
|Master Data|users|ユーザー|
|Master Data|hotels|ホテル|
|Master Data|projects|Project|
|Master Data|room_types|RoomType|
|Master Data|rooms|Room|
|Business Data|issues|Issue|
|Business Data|comments|Comment|
|Business Data|attachments|Attachment|

---

## 4.2 Entity Relationship Overview

```text
User
 ├── Issue
 ├── Comment
 └── Attachment

Hotel
 ├── Project
 ├── RoomType
 └── Room

Project
 └── Issue
      ├── Comment
      ├── Attachment
      └── Room (optional reference)

RoomType
 └── Room
```

---

## 4.3 Data Classification

本システムのデータは以下に分類する。

### Master Data

システム運用の基礎となる管理データである。

- User
- Hotel
- Project
- RoomType
- Room

### Business Data

コミッショニング業務で日々登録・更新されるデータである。

- Issue
- Comment
- Attachment

---

# 5. Design Policy

## 5.1 Database

初期版では SQLite を利用する。

ただし、将来的に PostgreSQL へ移行できるよう、DB 依存の実装を最小限に抑える。

---

## 5.2 ID

各テーブルは整数の主キー `id` を持つ。

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
```

---

## 5.3 Timestamp

日時は UTC で管理する。

Timestamp の生成および更新は Python 側で行い、SQLite 固有の日時関数には依存しない。

SQLite には、UTC を表す timezone-naive datetime を保存する。

アプリケーション内で Timestamp を生成する際は、UTC の timezone-aware datetime を生成した後、DB 保存前に timezone 情報を除去する。

|カラム|用途|設定方針|
|---|---|---|
|created_at|作成日時|Entity 作成時に Python 側で設定する。|
|updated_at|更新日時|Entity 作成時に設定し、更新処理時に Service Layer から明示的に更新する。|
|uploaded_at|ファイルアップロード日時|Attachment 作成時に Python 側で設定する。|

以下の方針を採用する。

- DB の `server_default` は使用しない。
- ORM Event による自動更新は行わない。
- DB と Python の両方へ重複して default を定義しない。
- Timestamp は NULL 不可とする。
- DB から取得した timezone-naive datetime は UTC として扱う。

---

## 5.4 Delete Policy

初期版では、業務上重要なデータの削除は最小限とする。

|データ|削除方針|
|---|---|
|Issue|削除しない|
|Comment|削除しない|
|Attachment|削除可能|
|Master Data|初期版では画面削除なし|

---

## 5.5 Master Data Management

初期版では、Master Data は CLI または CSV で管理する。

Web 画面による Master Data 管理は初期版では実装しない。

---

## 5.6 Business Rule Validation

DB 制約だけで表現しにくい業務ルールは Service 層で検証する。

例：

- 同一 Hotel 内で Room Numberが重複しないこと。
- Issue の Room 参照は任意であること。
- Target Type と対象カラムの整合性。
- Issue 作成時の必須項目。
- Attachment のファイル種別・サイズ制限。

---

## 5.7 File Storage

添付ファイル本体は DB には保存しない。

DB にはファイルのメタデータのみ保存する。

ファイル本体は Local Storage へ保存する。

`file_path` は絶対パスではなく相対パスで保存する。

---

## 5.8 Enum Storage Policy

Role、Target Type、Category および Status は Python Enum として定義する。

DB には Enum の文字列値を TEXT として保存する。

保存値は各設計書で定義された大文字の文字列と一致させる。

例：

```text
ENGINEER
ROOM
LIGHTING
OPEN
```

定義済み値以外の保存を防ぐため、対象カラムには CHECK 制約を設定する。

DB ネイティブの Enum 型は使用しない。

---

## 5.9 Foreign Key and Relationship Policy

Foreign Key には `ON DELETE` を明示的に指定しない。

初期版では、SQLAlchemy の `relationship` に削除 cascade および `delete-orphan` を設定しない。

削除方針は以下のとおりとする。

- Issue は削除しない。
- Comment は削除しない。
- Attachment の削除はアプリケーション側で明示的に処理する。
- Master Data の削除は初期版の Web 機能として提供しない。

ORM の `relationship` は参照およびデータ取得のために使用し、暗黙的な関連データ削除には使用しない。

---

## 5.10 Migration Policy

既存の Alembic Migration 履歴は維持する。

適用済みまたはコミット済みの Migration は削除、統合、置換しない。

データベース設計の変更は、既存 Migration の後続となる新しい Migration として追加する。

Database Models 実装では、既存スキーマを最新版の Database Design に合わせる追加 Migration を作成する。

Migration は以下を満たすこと。

- 既存の Migration から `upgrade` できること。
- 最新 Revision から直前の Revision へ `downgrade` できること。
- 新規の空データベースに対して、先頭から最新 Revision まで `upgrade` できること。
- Migration 履歴を作り直さないこと。

初期開発フェーズでは、既存の開発用データの互換性は保証しない。

初期開発フェーズでは、既存の `users` テーブルに業務データは存在しないことを前提とする。

そのため、`password_hash` を含む新しい必須カラムの追加に伴う既存データ移行は実施しない。

既存テーブルへ新しい必須カラムを追加する場合、既存レコードの移行値は設定しない。必要に応じて開発用データベースを削除し、新規の空データベースに対して Migration を適用する。

---

# 6. Master Data Tables

本章では、システムの基礎となる Master Data テーブルを定義する。

---

# 6.1 users

システムユーザーを管理する。

## Purpose

認証および認可の対象となるユーザー情報を保持する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|username|TEXT|No|ログイン ID|
|password_hash|TEXT|No|パスワードハッシュ|
|display_name|TEXT|No|表示名|
|role|TEXT|No|Administrator / Engineer|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Constraints

- username は一意とする。
- role は定義済みRoleのみ許可する。

---

# 6.2 hotels

Hotel を管理する。

## Purpose

コミッショニング対象となる施設を管理する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|name|TEXT|No|ホテル名|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Constraints

なし

---

# 6.3 projects

Project を管理する。

## Purpose

コミッショニング案件を管理する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|hotel_id|INTEGER|No|Hotel|
|name|TEXT|No|Project 名|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|hotel_id|hotels.id|

## Constraints

- hotel_id は必須とする。

---

# 6.4 room_types

RoomType を管理する。

## Purpose

Room の種別を管理する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|hotel_id|INTEGER|No|Hotel|
|name|TEXT|No|RoomType 名|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|hotel_id|hotels.id|

## Constraints

- hotel_id は必須とする。

---

# 6.5 rooms

Room を管理する。

## Purpose

Hotel 内で管理する部屋情報を保持する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|hotel_id|INTEGER|No|Hotel|
|room_type_id|INTEGER|No|RoomType|
|room_number|TEXT|No|部屋番号|
|display_name|TEXT|Yes|表示名|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|hotel_id|hotels.id|
|room_type_id|room_types.id|

## Constraints

- hotel_id は必須とする。
- room_number は必須とする。
- room_type_id は必須とする。

同一 Hotel 内では room_number を一意とする。

---

# 6.6 Master Data Relationships

Master Data 間のリレーションを以下に示す。

```text
Hotel
 ├── Project
 ├── RoomType
 └── Room

RoomType
 └── Room
```

---

## 6.7 Relationship Summary

|親テーブル|子テーブル|関係|
|---|---|---|
|hotels|projects|1 : N|
|hotels|room_types|1 : N|
|hotels|rooms|1 : N|
|room_types|rooms|1 : N|

---

## 6.8 Management Policy

初期版では以下の Master Data を CLI または CSV で管理する。

- User
- Hotel
- Project
- RoomType
- Room

Web 画面による管理機能は提供しない。

---

# 7. Business Data Tables

本章では、コミッショニング業務で利用する Business Data テーブルを定義する。

Issue を集約ルート(Aggregate Root)とし、Comment および Attachment は Issue に従属する。

---

# 7.1 issues

Issue を管理する。

## Purpose

コミッショニング時に発生した課題、確認事項および改善項目を管理する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|project_id|INTEGER|No|Project|
|room_id|INTEGER|Yes|Room|
|target_type|TEXT|No|Target Type|
|target|TEXT|Yes|対象名|
|category|TEXT|No|Category|
|description|TEXT|No|詳細説明|
|status|TEXT|No|Issue 状態|
|created_by|INTEGER|No|登録者|
|updated_by|INTEGER|No|更新者|
|created_at|DATETIME|No|作成日時|
|updated_at|DATETIME|No|更新日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|project_id|projects.id|
|room_id|rooms.id|
|created_by|users.id|
|updated_by|users.id|

## Constraints

- project_id は必須とする。
- room_id は任意とする。
- description は必須とする。
- target_type は定義済み Target Type のみ許可する。
- category は定義済み Category のみ許可する。
- status は定義済み Status のみ許可する。
- Target Type と `room_id` および `target` の組み合わせは、以下の業務ルールに従う。
  - `ROOM` の場合、`room_id` を指定し、`target` は null とする。
  - `OTHER` の場合、`room_id` は null とし、`target` に対象名を保存する。
- 上記の組み合わせは Service Layer で検証する。
- 上記の組み合わせに対する複合 CHECK 制約は DB へ定義しない。

---

# 7.2 comments

Comment を管理する。

## Purpose

Issue に対するコメント履歴を保持する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|issue_id|INTEGER|No|Issue|
|comment|TEXT|No|コメント|
|created_by|INTEGER|No|登録者|
|created_at|DATETIME|No|作成日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|issue_id|issues.id|
|created_by|users.id|

## Constraints

- issue_id は必須とする。
- comment は必須とする。

Comment は履歴データであるため、更新日時(updated_at)は保持しない。

---

# 7.3 attachments

Attachment を管理する。

## Purpose

Issue へ添付した写真・動画を管理する。

## Columns

|カラム|型|NULL|説明|
|---|---|---|---|
|id|INTEGER|No|主キー|
|issue_id|INTEGER|No|Issue|
|file_name|TEXT|No|保存ファイル名|
|original_file_name|TEXT|No|元ファイル名|
|file_path|TEXT|No|相対保存パス|
|mime_type|TEXT|No|MIME Type|
|file_size|INTEGER|No|ファイルサイズ(Byte)|
|uploaded_by|INTEGER|No|登録者|
|uploaded_at|DATETIME|No|アップロード日時|

## Foreign Keys

|カラム|参照先|
|---|---|
|issue_id|issues.id|
|uploaded_by|users.id|

## Constraints

- issue_id は必須とする。
- file_name は必須とする。
- file_path は必須とする。
- file_size は0 より大きい値とする。

添付ファイル本体は Local Storage に保存し、本テーブルではメタデータのみ管理する。

---

# 7.4 Business Data Relationships

Business Data 間のリレーションを以下に示す。

```text
Project
 └── Issue
      ├── Comment
      ├── Attachment
      └── Room (optional reference)

User
 ├── Issue
 ├── Comment
 └── Attachment
```

---

## 7.5 Relationship Summary

|親テーブル|子テーブル|関係|
|---|---|---|
|projects|issues|1 : N|
|rooms|issues|任意参照|
|users|issues|1 : N|
|issues|comments|1 : N|
|users|comments|1 : N|
|issues|attachments|1 : N|
|users|attachments|1 : N|

---

## 7.6 Aggregate Design

Issue を Aggregate Root とする。

Comment および Attachment は単独では存在できず、必ず Issue に属する。

Issue を削除しない運用とするため、Comment および Attachment も業務データとして保持される。

Business Data の整合性は Issue を中心として維持する。

---

# 8. Constraints

本章では、データベース設計における制約を定義する。

---

## 8.1 Primary Keys

すべてのテーブルは単一の主キー `id` を持つ。

|テーブル|主キー|
|---|---|
|users|id|
|hotels|id|
|projects|id|
|room_types|id|
|rooms|id|
|issues|id|
|comments|id|
|attachments|id|

---

## 8.2 Foreign Keys

各テーブルの外部キーを以下に示す。

|テーブル|外部キー|参照先|
|---|---|---|
|projects|hotel_id|hotels.id|
|room_types|hotel_id|hotels.id|
|rooms|hotel_id|hotels.id|
|rooms|room_type_id|room_types.id|
|issues|project_id|projects.id|
|issues|room_id|rooms.id|
|issues|created_by|users.id|
|issues|updated_by|users.id|
|comments|issue_id|issues.id|
|comments|created_by|users.id|
|attachments|issue_id|issues.id|
|attachments|uploaded_by|users.id|

---

## 8.3 Unique Constraints

|テーブル|制約|
|---|---|
|users|username|
|rooms|(hotel_id, room_number)|

---

## 8.4 Delete Policy

初期版では、業務データの削除は最小限とする。

|テーブル|削除方針|
|---|---|
|users|CLI または CSV による管理|
|hotels|CLI または CSV による管理|
|projects|CLI または CSV による管理|
|room_types|CLI または CSV による管理|
|rooms|CLI または CSV による管理|
|issues|削除しない|
|comments|削除しない|
|attachments|削除可能|

---

## 8.5 Constraint Naming

制約名は以下の形式とする。

|種類|形式|例|
|---|---|---|
|Primary Key|`pk_<table>`|`pk_users`|
|Foreign Key|`fk_<table>_<column>_<referred_table>`|`fk_projects_hotel_id_hotels`|
|Unique Constraint|`uq_<table>_<column>`|`uq_users_username`|
|複合Unique Constraint|`uq_<table>_<column1>_<column2>`|`uq_rooms_hotel_id_room_number`|
|Check Constraint|`ck_<table>_<purpose>`|`ck_attachments_file_size_positive`|

Alembic と SQLAlchemy で同一の命名規則を使用する。

---

## 9. Indexes

検索性能向上のため、以下のインデックスを作成する。

Index 名は以下の形式とする。

```text
ix_<table>_<column>
```

例：

```text
ix_projects_hotel_id
ix_room_types_hotel_id
ix_rooms_hotel_id
ix_issues_project_id
ix_issues_room_id
ix_issues_status
ix_issues_category
ix_issues_target_type
ix_comments_issue_id
ix_attachments_issue_id
```

|テーブル|カラム|用途|
|---|---|---|
|projects|hotel_id|Hotel 検索|
|room_types|hotel_id|RoomType 検索|
|rooms|hotel_id|Hotel 内 Room 検索|
|issues|project_id|Project 内 Issue 検索|
|issues|room_id|Room 別 Issue 検索|
|issues|status|Status 検索|
|issues|category|Category 検索|
|issues|target_type|Target Type 検索|
|comments|issue_id|Issue 別 Comment 検索|
|attachments|issue_id|Issue 別 Attachment 検索|

---

# 10. Repository Policy

Repository はデータアクセスのみを担当する。

## Responsibilities

Repository は以下を担当する。

- データ取得
- データ登録
- データ更新
- データ削除
- 検索

Repository では業務ロジックを実装しない。

---

## Repository Structure

各Aggregateごとに Repository を定義する。

```text id="m31w9v"
UserRepository

ProjectRepository

RoomRepository

IssueRepository
```

Comment および Attachment は Issue Aggregateに属するため、必要に応じて専用 Repository を設ける。

---

# 11. Service Validation Policy

業務ルールは Service Layer で検証する。

## Validation Examples

Service Layer では以下を検証する。

- 必須項目
- Target Type
- Category
- Status
- Room 存在確認
- Project 存在確認
- User 存在確認
- Attachment のサイズ
- Attachment の拡張子
- 業務ルール

DB 制約では表現できないルールは Service Layer で実装する。

---

# 12. Future Enhancements

将来的な拡張を以下に示す。

- PostgreSQL への移行
- Full Text Search 対応
- 添付ファイル保存先の変更(NAS ・クラウドストレージ)
- Audit Log テーブル追加
- Notification テーブル追加
- AI実行履歴テーブル追加
- Soft Delete 対応
- 履歴管理テーブル追加

これらは初期版の設計範囲には含めない。

---

# End of Document
