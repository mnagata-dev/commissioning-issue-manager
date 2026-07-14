# CIM UI Design

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-09
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Reflect updated login specification and master data terminology.|
|1.2|2026-07-09|Align UI design with Requirements v1.2. Simplify Target Type to ROOM and OTHER, clarify AI Draft workflow, add validation rules, and improve Issue Detail and Issue Edit screens.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. UI Design Policy
5. Screen List
6. Screen Navigation
7. Common UI Components
8. Login
9. Project Selection
10. Issue List
11. Issue Detail
12. Issue Create
13. Issue Edit
14. Administration
15. Error Display
16. Future Enhancements

---

# 1. Purpose

本書は、CIM (Commissioning Issue Manager) の UI 設計を定義することを目的とする。

本書では、画面一覧、画面遷移、各画面の表示項目、入力項目、および操作仕様を定義する。

---

# 2. Scope

本書では以下を対象とする。

- 画面一覧
- 画面遷移
- 共通 UI 方針
- 各画面の表示項目
- 各画面の入力項目
- 各画面の操作仕様
- エラー表示方針

以下は対象外とする。

- API 詳細仕様
- DB 設計
- CSS 詳細
- JavaScript 実装詳細
- テストケース

これらは各設計書で定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

|ドキュメント|説明|
|---|---|
|requirements.md|要件定義書|
|basic_design.md|基本設計書|
|api_design.md|API 設計書|
|project_conventions.md|プロジェクト共通ルール|

---

# 4. UI Design Policy

## 4.1 Mobile First

本システムはコミッショニング現場で利用されるため、スマートフォン利用を重視する。

PC ブラウザでも利用可能とする。

---

## 4.2 Simple UI

初期版では、複雑な UI コンポーネントを避け、シンプルで分かりやすい画面構成とする。

---

## 4.3 Issue First

本システムの中心は Issue 管理である。

画面設計では、Issue の登録・確認・更新を最優先とする。

---

## 4.4 User in Control

AI Draftは補助機能である。

AIが生成した内容は、必ずユーザーが確認・修正してから保存する。

---

# 5. Screen List

初期版で提供する画面を以下に示す。

|画面|説明|
|---|---|
|Login|ログイン画面|
|Project Selection|Project 選択画面|
|Issue List|Issue 一覧画面|
|Issue Detail|Issue 詳細画面|
|Issue Create|Issue 登録画面|
|Issue Edit|Issue 編集画面|
|Administration|管理メニュー画面|

---

# 6. Screen Navigation

画面遷移を以下に示す。

```text
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

# 7. Common UI Components

本システムで共通利用する UI コンポーネントを以下に示す。

|コンポーネント|用途|
|---|---|
|Header|画面タイトル、ログアウト、現在の Project 表示|
|Navigation|主要画面への遷移|
|Button|保存、戻る、削除、追加などの操作|
|Form|入力フォーム|
|Modal|確認ダイアログ|
|Alert|エラー・警告・成功メッセージ|
|Loading|API 通信中表示|
|Badge|Status や Category 表示|

---

## 7.1 Header

Headerには以下を表示する。

- システム名
- 現在の Project
- ログインユーザー
- Logout ボタン

---

## 7.2 Button

主要操作には明確なラベルを表示する。

例：

- Save
- Cancel
- Back
- Add Comment
- Upload Attachment
- Generate AI Draft

---

## 7.3 Alert

エラーや成功メッセージは画面上部または該当フォーム付近に表示する。

ユーザーが理解しやすい文言を使用する。

---

## 7.4 Loading

API 通信中または AI Draft 生成中は Loading 表示を行う。

AI Draft 生成中は、ユーザーが処理中であることを認識できる表示とする。

---

# 8. Login

## 8.1 Purpose

ユーザー認証を行う。

認証成功後、Project Selection 画面へ遷移する。

---

## 8.2 Screen Layout

```text
+--------------------------------------------------+
|                  CIM Login                       |
+--------------------------------------------------+

Username
+----------------------------------------------+

Password
+----------------------------------------------+

[ Login ]

--------------------------------------------------

Error Message
```

---

## 8.3 Display Items

|項目|説明|
|---|---|
|Username|ログイン ID (メールアドレス形式も可)|
|Password|パスワード入力|
|Login Button|ログイン実行|
|Error Message|認証失敗時に表示|

---

## 8.4 Operations

|操作|内容|
|---|---|
|Login|認証を実行する。|
|Enter Key|ログインを実行する。|

---

# 9. Project Selection

## 9.1 Purpose

作業対象となる Project を選択する。

---

## 9.2 Screen Layout

```text
+--------------------------------------------------+
| Project Selection                                |
+--------------------------------------------------+

Current User

----------------------------------------

Project List

○ Hotel A Commissioning

○ Hotel B Commissioning

○ Hotel C Commissioning

----------------------------------------

[ Select Project ]
```

---

## 9.3 Display Items

|項目|説明|
|---|---|
|Current User|ログイン中のユーザー|
|Project List|選択可能な Project 一覧|
|Select Project Button|Project 決定|

---

## 9.4 Operations

|操作|内容|
|---|---|
|Select Project|Project を選択する。|
|Confirm|Issue List 画面へ遷移する。|

---

# 10. Issue List

## 10.1 Purpose

選択中 Project の Issue 一覧を表示する。

Issue 検索および Issue 登録の起点となる画面である。

---

## 10.2 Screen Layout

```text
+--------------------------------------------------+
| Project : Hotel A Commissioning                  |
+--------------------------------------------------+

Search

Keyword
+--------------------------+

Status
[ OPEN ▼ ]

Category
[ LIGHTING ▼ ]

[ Search ]

--------------------------------------------------

Issue List

--------------------------------------------------
OPEN

Room 1203

Bathroom light does not turn off.

2026-06-30
--------------------------------------------------

OPEN

Room 1205

Curtain does not close.

2026-06-30

--------------------------------------------------

OPEN

Target : Network

Processor cannot communicate with gateway.

2026-06-30

--------------------------------------------------

[ + New Issue ]
```

---

## 10.3 Display Items

|項目|説明|
|---|---|
|Current Project|選択中 Project|
|Search Conditions|検索条件|
|Issue List|Issue 一覧|
|Status Badge|Status 表示|
|New Issue Button|Issue 登録画面へ遷移|

---

## 10.4 Search Conditions

|項目|必須|説明|
|---|:-:|---|
|Keyword|No|キーワード検索|
|Status|No|Status|
|Category|No|Category|
|Target Type|No|Target Type|

---

## 10.5 Issue List Item

各Issueには以下を表示する。

|項目|説明|
|---|---|
|Status|現在の状態|
|Room|Target Type が ROOM の場合に表示する|
|Target|Target Type が OTHER の場合に表示する対象名|
|Category|Category|
|Description|Issue 内容の先頭部分|
|Updated At|最終更新日時|

---

## 10.6 Operations

|操作|内容|
|---|---|
|Search|条件検索を行う。|
|Open Issue|Issue Detail 画面へ遷移する。|
|New Issue|Issue Create 画面へ遷移する。|
|Change Project|Project Selection 画面へ戻る。|

---

# 11. Issue Detail

## 11.1 Purpose

登録済み Issue の詳細情報を表示する。

Comment および Attachment も合わせて表示し、Issue の状況を確認できる。

---

## 11.2 Screen Layout

Target Type = ROOM

```text
+--------------------------------------------------+
| Issue Detail                                     |
+--------------------------------------------------+

Status : OPEN

Room : 1203

Target Type : ROOM

Category : LIGHTING

Description

Bathroom light remains on after Master OFF.

--------------------------------------------------

Comments

----------------------------------------
Engineer 1

Checked on site.

2026-06-30 10:20
----------------------------------------

--------------------------------------------------

Attachments

photo_001.jpg

video_001.mp4

--------------------------------------------------

[ Edit ]
[ Add Comment ]
[ Upload Attachment ]
[ Back ]
```

Target Type = OTHER

```text
+--------------------------------------------------+
| Issue Detail                                     |
+--------------------------------------------------+

Status : OPEN

Target Type : OTHER

Target : Network

Category : NETWORK

Description

Processor cannot communicate with gateway.

--------------------------------------------------

Comments

----------------------------------------
Engineer 1

Checked on site.

2026-06-30 10:20
----------------------------------------

--------------------------------------------------

Attachments

photo_001.jpg

video_001.mp4

--------------------------------------------------

[ Edit ]
[ Add Comment ]
[ Upload Attachment ]
[ Back ]
```

---

## 11.3 Display Items

|項目|説明|
|---|---|
|Status|Issue の状態|
|Room|Target Type が ROOM の場合に表示する|
|Target Type|Target Type|
|Target|Target Type が OTHER の場合に表示する対象名|
|Category|Category|
|Description|詳細説明|
|Comment List|コメント履歴|
|Attachment List|添付ファイル一覧|

---

## 11.4 Operations

|操作|内容|
|---|---|
|Edit|Issue Edit 画面へ遷移する。|
|Add Comment|Comment を追加する。|
|Upload Attachment|Attachment を追加する。|
|Open Attachment|添付ファイルを表示する。|
|Back|Issue Listへ戻る。|

---

# 12. Issue Create

## 12.1 Purpose

新しい Issue を登録する。

AI Draft を利用した入力支援を提供する。

---

## 12.2 Screen Layout

```text
+--------------------------------------------------+
| New Issue                                        |
+--------------------------------------------------+

Target Type
[ ▼ ]

Room
[ ▼ ]
(Target Type = ROOM の場合)

Target
+--------------------------------------+
(Target Type = OTHER の場合)

Category
[ ▼ ]

Description

+--------------------------------------+
|                                      |
|                                      |
+--------------------------------------+

--------------------------------------------------

AI Draft

Input

+--------------------------------------+

[ Generate AI Draft ]

--------------------------------------------------

[ Save ]
[ Cancel ]
```

---

## 12.3 Display Items

|項目|説明|
|---|---|
|Target Type|Target Type 選択|
|Room|Target Type が ROOM の場合に表示|
|Target|Target Type が OTHER の場合に表示|
|Category|Category 選択|
|Description|詳細説明|
|AI Draft|AI 入力支援|

---

## 12.4 Operations

|操作|内容|
|---|---|
|Generate AI Draft|AI Draft を生成する。|
|Save|Issue を登録する。|
|Cancel|登録を中止する。|

---

## 12.5 AI Draft Flow

1. ユーザーが Target Type を選択する。
2. Target Type が ROOM の場合は Room を選択する。
3. Target Type が OTHER の場合は Target を入力する。
4. ユーザーが音声またはテキストを入力する。
5. 「 Generate AI Draft 」を押下する。
6. AI が入力内容を解析し、Category および Description を生成する。
7. ユーザーが生成結果を確認・修正する。
8. 「 Save 」を押下して Issue を登録する。

## 12.6 Validation

以下の項目を必須とする。

- Target Type
- Category
- Description

Target Type が ROOM の場合

- Room を必須とする。

Target Type が OTHER の場合

- Target を必須とする。

入力内容がバリデーションルールを満たさない場合は、保存を行わず、該当項目にエラーメッセージを表示する。

---

# 13. Issue Edit

## 13.1 Purpose

登録済み Issue を更新する。

---

## 13.2 Screen Layout

```text
+--------------------------------------------------+
| Edit Issue                                       |
+--------------------------------------------------+

Status
[ OPEN ▼ ]

Target Type
[ ▼ ]

Room
[ ▼ ]
(Target Type = ROOM の場合)

Target
+--------------------------------------+
(Target Type = OTHER の場合)

Category
[ ▼ ]

Description

+--------------------------------------+
|                                      |
|                                      |
+--------------------------------------+

--------------------------------------------------

[ Save ]
[ Cancel ]
```

---

## 13.3 Display Items

Issue Create 画面と同様の入力項目を表示する。

編集画面では、既存の Issue の内容を初期値として表示し、利用者は必要な項目を変更できる。

|項目|説明|
|---|---|
|Status|Issue の現在の状態を表示・編集する。|
|Target Type|Target Type を選択する。|
|Room|Target Type が ROOM の場合に表示する。|
|Target|Target Type が OTHER の場合に表示する。|
|Category|Category を選択する。|
|Description|Issue の詳細説明を入力・編集する。|

---

## 13.4 Operations

|操作|内容|
|---|---|
|Save|Issue を更新する。|
|Cancel|編集を中止する。|
|Change Status|Status を変更する。|

---

## 13.5 Validation

以下の項目を必須とする。

- Target Type
- Category
- Description

Target Type が ROOM の場合

- Room を必須とする。

Target Type が OTHER の場合

- Target を必須とする。

入力内容がバリデーションルールを満たさない場合は、保存を行わず、該当項目にエラーメッセージを表示する。

---

# 14. Administration

## 14.1 Purpose

Administrator 向けの管理機能を提供する。

初期版では、Project 管理、User 管理および Master Data 管理は CLI または CSV で実施するため、本画面は管理機能の入口として提供する。

---

## 14.2 Screen Layout

```text
+--------------------------------------------------+
| Administration                                   |
+--------------------------------------------------+

System Administration

--------------------------------------------

Project Management

(Currently managed via CLI / CSV)

--------------------------------------------

User Management

(Currently managed via CLI / CSV)

--------------------------------------------

Master Data Management

(Currently managed via CLI / CSV)

--------------------------------------------

[ Back ]
```

---

## 14.3 Display Items

|項目|説明|
|---|---|
|Project Management|Project 管理機能|
|User Management|User 管理機能|
|Master Data Management|Hotel、RoomType、Room などの管理|
|Back Button|前画面へ戻る|

---

## 14.4 Operations

|操作|内容|
|---|---|
|Back|前画面へ戻る。|

初期版では Web 画面からの更新機能は提供しない。

---

# 15. Error Display

## 15.1 Purpose

ユーザーがエラー内容を理解し、適切な対応を行えるようにする。

---

## 15.2 Display Policy

- エラーメッセージはユーザーに理解しやすい表現とする。
- システム内部の詳細情報は表示しない。
- 入力エラーは対象項目の近くに表示する。
- システムエラーは画面上部に表示する。

---

## 15.3 Validation Errors

例：

```text
Room を選択してください。

Category を選択してください。

Description を入力してください。
```

---

## 15.4 Authentication Error

例：

```text
ログイン ID またはパスワードが正しくありません。
```

---

## 15.5 System Error

例：

```text
予期しないエラーが発生しました。

時間をおいて再度お試しください。
```

---

## 15.6 AI Error

例：

```text
AI Draft の生成に失敗しました。

入力内容を確認して再度実行してください。
```

---

# 16. Future Enhancements

将来的に以下のUI改善を検討する。

- Web 画面による Project 管理
- Web 画面による User 管理
- Web 画面による Master Data 管理
- Dashboard 画面
- Issue 統計画面
- AI チャット画面
- ダークモード対応
- 多言語対応
- タブレット向けレイアウト最適化
- アクセシビリティ向上

これらは初期版の設計範囲には含めない。

---

# End of Document
