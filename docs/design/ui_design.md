# CIM UI Design

- **Document Version:** 1.3
- **Status:** Draft
- **Last Updated:** 2026-10-07
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Reflect updated login specification and master data terminology.|
|1.2|2026-07-09|Align UI design with Requirements v1.2. Simplify Target Type to ROOM and OTHER, clarify AI Draft workflow, add validation rules, and improve Issue Detail and Issue Edit screens.|
|1.3|2026-09-29|Align UI design with Requirements v1.3, Basic Design v1.3, and API Design v1.3 for local voice transcription, Voice / Text Input, and the AI Draft workflow.|
|1.3|2026-10-01|Clarify Voice Input recording start and stop operations before local voice transcription.|
|1.3|2026-10-07|Specify Input Assistance defaults and OTHER Target history for Issue Create, and preserve Issue Edit current values.|

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

## 5.1 Screen URLs

初期版の主要画面URLを以下に示す。

|画面|URL|
|---|---|
|Login|`/`|
|Project Selection|`/projects.html`|
|Issue List|`/issues.html`|
|Issue Detail|`/issue.html?issue_id={issue_id}`|
|Issue Create|`/issue-create.html`|
|Issue Edit|`/issue-edit.html?issue_id={issue_id}`|

その他の画面URLは、各画面の実装前に定義する。

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

## 6.1 Authentication and Selection Navigation

画面遷移は以下のルールに従う。

- Login 成功後は Project Selection 画面へ遷移する。
- 認証済みユーザーが Login 画面を表示した場合は、Project Selection 画面へ遷移する。
- 認証が必要な画面で未認証または Session 期限切れを検出した場合は、Login 画面へ遷移する。
- Project を選択していない状態で Issue List 画面を表示した場合は、Project Selection 画面へ遷移する。
- 選択した Project は、同一ブラウザセッション中の画面遷移で維持する。

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
|Login|認証を実行する。認証成功後は Project Selection 画面へ遷移する。|
|Enter Key|ログインを実行する。|
|Open Login while Authenticated|認証済みの場合は Project Selection 画面へ遷移する。|

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
|Select Project|作業対象となる Project を選択する。|
|Confirm|選択した Project を同一ブラウザセッション中に保持し、Issue List 画面へ遷移する。|
|Open without Authentication|Login 画面へ遷移する。|

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

初期表示時は検索条件を指定せず、選択中 Project の Issue をすべて表示する。

Status、Category および Target Type には `All` を選択肢として用意する。

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
|Search|条件検索を行う。検索実行時は1ページ目を表示する。|
|Open Issue|Issue Detail 画面へ遷移する。|
|New Issue|Issue Create 画面へ遷移する。|
|Previous Page|前のページを表示する。|
|Next Page|次のページを表示する。|
|Change Project|Project Selection 画面へ戻る。|
|Open without Selected Project|Project Selection 画面へ遷移する。|
|Open without Authentication|Login 画面へ遷移する。|

初期版では `page_size` を `20` に固定する。

前後のページが存在しない場合は、対応するページ移動操作を無効にする。

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
|Add Comment|Issue Detail 画面内で Comment 入力欄を表示し、Comment を追加する。|
|Upload Attachment|Issue Detail 画面内でファイルを選択し、Attachment を追加する。|
|Open Attachment|添付ファイルを表示する。|
|Back|Issue Listへ戻る。|
|Open without Issue ID|Issue ID が指定されていない、または不正な場合は Issue List 画面へ遷移する。|
|Issue Not Found|Issue が存在しない場合は Issue List 画面へ遷移する。|
|Open without Authentication|未認証または Session 期限切れの場合は Login 画面へ遷移する。|

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

[ Voice Input ]
(録音中: [ Stop Recording ])

Voice / Text Input

+--------------------------------------+
| 文字起こし結果または直接入力テキスト   |
| (編集可能)                           |
+--------------------------------------+

[ Generate AI Draft ]

--------------------------------------------------

[ Save ]
[ Cancel ]
```

Voice Input で録音を開始し、録音中は Stop Recording で明示的に録音を終了する。録音終了後に音声を Speech Transcription API へ送信し、ローカル文字起こし結果を Voice / Text Input に表示する。ユーザーは同じ入力欄で必要に応じて修正するか、直接テキストを入力し、Generate AI Draft を明示的に実行する。

生成結果は上部の Category / Description に反映し、ユーザーが確認・必要に応じて修正した後、Save で Issue を登録する。詳細な操作の流れは 12.5 AI Draft Flow に従う。

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
|Voice Input|録音を開始するための操作|
|Stop Recording|録音中に表示し、ユーザーが明示的に録音を終了するための操作|
|Voice / Text Input|ローカル文字起こし結果を表示、またはユーザーが直接テキストを入力する。ユーザーが編集可能。|

---

## 12.4 Operations

|操作|内容|
|---|---|
|Voice Input|音声の録音を開始する。|
|Stop Recording|録音を終了し、録音した音声を Speech Transcription API へ送信する。Local Speech Recognition による文字起こし成功後、response の text を Voice / Text Input に表示する。|
|Generate AI Draft|ユーザーが Voice / Text Input を確認し、必要に応じて修正した後、そのテキストから AI Draft を生成する。文字起こし完了後に自動実行しない。|
|Save|Issue を登録する。|
|Cancel|登録を中止する。|

音声認識処理中は、ユーザーが処理中であることを認識できる表示とする。

音声認識はローカル環境で行い、インターネット接続および外部クラウドサービスを前提としない。

---

## 12.5 AI Draft Flow

1. ユーザーが Target Type を選択する。
2. Target Type が ROOM の場合は Room を選択する。
3. Target Type が OTHER の場合は Target を入力する。

入力方法ごとの流れを以下に示す。

```text
音声入力:
Voice Input → 録音開始 → Stop Recording → 録音終了
→ Speech Transcription API へ音声送信 → Local Speech Recognition → text
→ Voice / Text Input → ユーザーが必要に応じて修正 → Generate AI Draft

テキスト入力:
ユーザー入力 → Voice / Text Input
```

テキスト直接入力では Local Speech Recognition を経由しない。

文字起こし結果の確認・修正は既存の Voice / Text Input で行い、独立した確認画面や必須確認操作は設けない。文字起こし完了後に Generate AI Draft を自動実行しない。

入力後は以下の共通フローとする。

1. ユーザーが「 Generate AI Draft 」を押下する。
2. AI が Voice / Text Input のテキストを解析し、Category と日本語の Description を生成する。
3. ユーザーが Category / Description を確認し、必要に応じて修正する。
4. ユーザーが「 Save 」を押下して Issue を登録する。

AI は音声そのものを解析せず、Target Type、Room、Target を決定しない。

AI Draft は入力支援であり、Issue を自動登録しない。最終的な登録内容はユーザーが決定する（User in Control）。

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

## 12.7 Input Assistance

Requirements v1.3 §7.12 の入力支援として、Issue Create を開いたとき、現在選択中の Project の前回利用値を Target Type、Room、Category の初期値として表示する。

Room は現在の Project で選択可能な場合だけ復元する。保存値が存在しない、無効、または現在利用できない項目は復元せず、その項目を通常の初期状態とする。

Target Type が OTHER の場合、現在の Project の過去の Target 入力履歴を候補として表示し、ユーザーが選択できるようにする。候補を使用せず自由入力することもできる。Target はユーザーが決定し、AI は推測・自動決定しない。

保存先はブラウザの localStorage とする。Issue の登録成功時だけ、登録に使用した前回利用値を保存し、OTHER の場合は Target を履歴へ追加する。Project 単位の保存・復元処理は Detailed Design §6.3 に従う。

localStorage が利用できない場合は入力支援だけを利用できない状態とし、通常の入力・Issue 登録は継続できるようにする。

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

localStorage の前回利用値で編集対象 Issue の現在値を上書きしない。Issue Edit の更新成功時も、前回利用値および OTHER Target 入力履歴は更新しない。

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

## 15.7 Speech Recognition Error

音声認識に失敗した場合は、AI Draft の生成エラーと区別し、ユーザーが理解できるエラーメッセージを表示する。

例：

```text
音声の文字起こしに失敗しました。

再度音声入力を行うか、Voice / Text Input にテキストを入力してください。
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
