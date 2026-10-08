# CIM Test Design

- **Document Version:** 1.4
- **Status:** Draft
- **Last Updated:** 2026-10-08
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Update authentication and master data related test cases.|
|1.2|2026-07-14|Align test design with Requirements v1.2, API Design, UI Design, and Detailed Design. Add validation, AI Draft, attachment, and business rule test cases.|
|1.3|2026-09-29|Add Local Speech Recognition / Speech Transcription tests, separation from AI Draft, Japanese Description, and User in Control coverage.|
|1.3|2026-10-07|Add UI verification cases for Project-scoped Input Assistance, Issue Edit isolation, and localStorage failures.|
|1.4|2026-10-08|Add Administration CLI, service and repository tests, including bootstrap, Administrator protection, transactions, and exit codes.|

---

# Table of Contents

1. Purpose
2. Scope
3. References
4. Test Policy
5. Test Levels
6. Test Environment
7. Unit Test
8. Service Test
9. Repository Test
10. API Test
11. UI Test
12. AI Test
13. File Upload Test
14. Error Handling Test
15. Authorization Test
16. Future Enhancements

---

# 1. Purpose

本書は、CIM (Commissioning Issue Manager) のテスト設計を定義することを目的とする。

本書では、テスト方針、テストレベル、テスト観点、および主要機能ごとのテスト内容を定義する。

本書を基に、pytestおよび手動テストを実施する。

---

# 2. Scope

本書では以下を対象とする。

- Unit Test
- Service Test
- Repository Test
- API Test
- UI Test
- AI Test
- Local Speech Recognition / Speech Transcription Test
- File Upload Test
- Error Handling Test
- Authorization Test
- Administration CLI Test

以下は対象外とする。

- 本番運用監視
- 負荷試験の詳細
- セキュリティ診断の詳細
- クラウド環境での試験

これらは将来必要になった時点で別途定義する。

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
|detailed_design.md|詳細設計書|
|project_conventions.md|プロジェクト共通ルール|
|ADR-001-user-in-control.md|User in Control の設計判断|

---

# 4. Test Policy

## 4.1 Basic Policy

CIM では、Service Layer と API を中心にテストする。

初期版では、自動テストと手動テストを併用する。

Local Speech Recognition / Speech Transcription は AI Draft と独立した機能として検証する。具体的な音声認識製品・モデルの精度評価、および実モデルの品質・精度・性能の新たな合否基準は本変更の対象外とする。

---

## 4.2 Priority

テスト優先度は以下の順とする。

1. Issue登録・更新
2. AI Draft
3. Attachment
4. Authentication
5. Comment
6. Project Selection
7. Administration

---

## 4.3 Automation Policy

自動化対象は以下とする。

- Service Test
- Repository Test
- API Test
- Validation Test
- Administration CLI Test
- username にメールアドレス形式を利用できること

UI の詳細操作は初期版では手動テストを中心とする。

Speech の Service / API 自動テストでは Local Speech Recognition boundary を Mock / Stub に置き換える。UI 自動テストを行う場合は API を Mock 化して画面フローを検証し、実際の microphone や Speech Recognition engine を必須としない。具体的なブラウザ録音 API や engine 固有のテスト方法は定義しない。

---

## 4.4 Offline Operation

Requirements 8.2 および Basic Design の Offline Operation に従い、以下を確認する。

|テスト項目|内容|
|---|---|
|Local Dependencies|設計・実装の確認により、Speech Transcription と AI Draft が外部クラウドサービスを必須とせず、必要なモデルと実行環境をローカルで利用すること|
|Automated Boundary Test|Mock / Stub を利用し、Speech と AI の独立した呼び出し・応答フローを自動テストで確認すること|
|Offline Manual Test|実装とローカル実行環境の準備後、インターネット接続のない環境で Speech Transcription と AI Draft の主要機能を利用できることを実機・手動で確認すること|

Mock / Stub のテストのみでは実環境のオフライン動作を確認済みとしない。具体的な runtime、executable、model、ネットワーク遮断手順は固定しない。

---

# 5. Test Levels

本システムでは以下のテストレベルを採用する。

|テストレベル|説明|
|---|---|
|Unit Test|小さな関数・メソッド単位のテスト|
|Service Test|業務ロジックのテスト|
|Repository Test|DB アクセスのテスト|
|API Test|REST API のテスト|
|UI Test|画面操作の確認|
|Manual Test|実利用に近い確認|

---

# 6. Test Environment

## 6.1 Development Test Environment

|項目|内容|
|---|---|
|OS|Windows 11 + WSL2 Ubuntu LTS|
|Backend|FastAPI|
|Database|SQLite|
|Test Framework|pytest|
|API Test|FastAPI TestClient|
|AI|Ollama または Mock|
|File Storage|Local Storage|

---

## 6.2 Test Database

テストでは本番用 DB とは別の SQLite DB を利用する。

テストごとにデータを初期化できる構成とする。

---

## 6.3 Test File Storage

Attachment テストでは、テスト専用の一時ディレクトリを利用する。

テスト終了後、作成ファイルを削除する。

---

# 7. Unit Test

本章では、単体テスト (Unit Test) の方針を定義する。

---

## 7.1 Purpose

小さな関数・ユーティリティ・バリデーション処理が期待どおり動作することを確認する。

---

## 7.2 Target

|対象|内容|
|---|---|
|Utility Functions|共通関数|
|Validation Functions|入力値検証|
|File Name Generator|保存ファイル名生成|
|Path Generator|保存パス生成|
|Enum Validation|Target Type、Category、Status の検証|

---

## 7.3 Test Items

|テスト項目|内容|
|---|---|
|Normal Case|正常入力|
|Boundary Value|境界値|
|Invalid Value|不正入力|
|Null|未入力|
|Exception|例外発生|

---

# 8. Service Test

本章では、Service Layer のテストを定義する。

Repository は Mock 化し、業務ロジックのみを検証する。

---

## 8.1 AuthService

|テスト項目|内容|
|---|---|
|Login Success|正常ログイン|
|Login Failure|認証失敗|
|Current User|ログインユーザー取得|

---

## 8.2 ProjectService

|テスト項目|内容|
|---|---|
|Project List|Project 一覧取得|
|Project Not Found|存在しない Project|

---

## 8.3 RoomService

|テスト項目|内容|
|---|---|
|Room List|指定 Hotel の Room 一覧取得|
|Empty Room List|Room が存在しない場合に空一覧を返すこと|
|Hotel Not Found|存在しない Hotel|

---

## 8.4 IssueService

|テスト項目|内容|
|---|---|
|Create Issue (ROOM)|Target Type = ROOM の正常登録|
|Create Issue (OTHER)|Target Type = OTHER の正常登録|
|Update Issue|正常更新|
|Change Status|Status 変更|
|Get Detail|詳細取得|
|List Issues|一覧取得|
|Invalid Target Type|不正な Target Type|
|ROOM without Room|Target Type = ROOM で Room 未指定|
|ROOM with Target|Target Type = ROOM で Target を指定|
|OTHER without Target|Target Type = OTHER で Target 未指定|
|OTHER with Room|Target Type = OTHER で Room を指定|
|Room and Project Mismatch|Room と Project が異なる Hotel に属する場合|
|Invalid Category|不正な Category|
|Invalid Status|不正な Status|
|Room Not Found|存在しない Room|
|Project Not Found|存在しない Project|

---

## 8.5 AIService

テキスト入力、SpeechService との責務分離、日本語 Description、および User in Control は12章、非永続化は10.10も確認する。

|テスト項目|内容|
|---|---|
|Generate Draft|正常生成|
|Empty Input|空入力|
|Ollama Error|AI 呼び出し失敗|
|Invalid Response|AI レスポンス不正|
|Target Information Ignored|AI が Target Type・Room・Target を返却しないこと|
|Unknown Category|Category を判定できない場合に OTHER を返却すること|

---

## 8.6 CommentService

|テスト項目|内容|
|---|---|
|Add Comment|正常登録|
|Empty Comment|空コメント|
|Issue Not Found|Issue 不存在|

---

## 8.7 AttachmentService

|テスト項目|内容|
|---|---|
|Upload Image|JPEG または PNG の画像を登録できること|
|Upload Video|MP4 または QuickTime の動画を登録できること|
|Delete Attachment|Attachment を削除できること|
|Issue Not Found|存在しない Issue へのアップロードまたは削除でエラーとなること|
|Attachment Not Found|存在しない Attachment の削除でエラーとなること|
|User Not Found|存在しない User によるアップロードまたは削除でエラーとなること|
|Invalid File Name|元ファイル名が不正な場合にエラーとなること|
|Invalid File Type|許可されていない MIME Type または拡張子を拒否すること|
|MIME Type and Extension Mismatch|MIME Type と拡張子の組み合わせが不正な場合にエラーとなること|
|Large Image|10 MiB を超える画像を拒否すること|
|Large Video|100 MiB を超える動画を拒否すること|
|Empty File|空ファイルを拒否すること|
|Upload Compensation|DB 登録失敗時に保存済みファイルを削除すること|
|Delete Staging|削除時に物理ファイルを `.trash/` へ一時退避してから DB 情報を削除すること|
|Delete Restore|DB 削除失敗時に `.trash/` のファイルを元の場所へ復元すること|

---

## 8.8 SpeechService

Local Speech Recognition boundary を Mock / Stub 化し、Detailed Design 10.10、12.8、13.5 に従って検証する。SpeechService のテストに DB / Repository / SQLAlchemy Session は不要とする。

|テスト項目|内容|
|---|---|
|Transcribe Audio|有効な audio を受け取り、Local Speech Recognition boundary を呼び出し、取得した transcription text を SpeechTranscriptionResponse の text として返すこと|
|Invalid Audio|audio が不正または利用できない場合、ValidationError とし、認識処理を呼び出さないこと|
|Recognition Failure|Local Speech Recognition の処理失敗を SpeechRecognitionError に変換すること|
|Unavailable Text|文字列でない、空、または利用可能な transcription text を取得できない場合、SpeechRecognitionError とすること|
|Responsibility Separation|AIService を呼び出さず、Category / Description を生成しないこと|
|No Target Decision|Project / Target Type / Room / Target を決定しないこと|
|No Persistence Dependency|DB / Repository / SQLAlchemy Session に依存せず、commit / rollback を行わないこと|
|No Business Side Effects|Issue を登録・更新せず、audio / transcription text を業務データとして永続化しないこと（10.10参照）|

---

## 8.9 AdministrationService

Detailed Design 10.11 に従い、Repository、認証・ハッシュ処理および Transaction 境界を Mock 化して Service の責務を検証する。実 DB での永続化・rollback・同時実行は9.5で検証する。

|テスト項目|内容|
|---|---|
|Create Hotel|name を指定して登録し、整数 ID と操作結果を返すこと|
|Update Hotel|name を更新し、ID と created_at を維持すること|
|Create Project|存在する Hotel と name を指定して登録できること|
|Update Project|name を更新し、hotel_id を維持すること|
|Create RoomType|存在する Hotel と name を指定して登録できること|
|Update RoomType|name を更新し、hotel_id を維持すること|
|Create Room|同一 Hotel の RoomType と room_number で登録し、display_name 省略時は null とすること|
|Update Room|room_number / display_name / 同一 Hotel の room_type_id を更新し、hotel_id を維持すること|
|Create User|username、display_name、Role、新しい Password を受け取り、既存 hash_password を利用して登録すること。メールアドレス形式の username も利用できること|
|Update User|username / display_name / Role / Password を指定した項目だけ更新し、省略した Role と Password Hash を維持すること|
|Partial Update|各対象で省略項目を維持し、ID / created_at を変更せず、変更時の updated_at は既存 UTC 方針に従うこと|
|No Update Fields|更新項目を指定しない場合はデータと Timestamp を維持して成功とすること|
|Authentication|通常操作は毎回 AuthService.login を利用し、username 不存在と Password 不一致を同じ AuthenticationError とすること|
|Authorization|5対象の create / update を Engineer は実行できず、AuthorizationError とすること。未認証・権限不足では書き込まないこと|
|Bootstrap Empty|User が0件の場合だけ未認証で bootstrap でき、Role は ADMINISTRATOR に固定されること|
|Bootstrap Existing User|Administrator または Engineer が1件でも存在する場合は BusinessRuleError とし、User を追加しないこと。Administrator が0人でも既存 User があれば拒否すること|
|Last Administrator|最後の Administrator の ENGINEER への変更は、自身を対象とする場合も BusinessRuleError とし、他の同時指定項目も保存しないこと|
|Multiple Administrators|Administrator が2人以上なら1人以上残る範囲で ENGINEER への変更を許可すること|
|Other Role Changes|Role 維持、ENGINEER から ADMINISTRATOR への変更、Administrator の追加は成功すること|
|Service Protection|CLI を経由しない update_user 呼び出しでも最後の Administrator 保護を適用すること|
|Required Fields and Types|登録必須項目の欠落、NULL 不可項目への null、不正な型 / Role を拒否すること。独自の一意性・文字数制限・Password policy を追加していないこと|
|Not Found|5対象それぞれの存在しない更新 ID と、存在しない参照 Hotel / RoomType を拒否すること|
|Hotel Consistency|Room 登録・RoomType 変更で別 Hotel の RoomType を拒否すること。Project / RoomType / Room の所属 Hotel を変更する入力を拒否すること|
|Duplicate Username|登録・更新とも別 User の username と重複する場合は失敗し、自身の username を維持する更新は成功すること|
|Duplicate Room Number|登録・更新とも同一 Hotel 内の別 Room と重複する場合は失敗し、自身の番号の維持と別 Hotel の同じ番号は成功すること|
|Duplicate Names Allowed|Hotel / Project / RoomType の name に独自の重複禁止を設けないこと|
|Transaction|1コマンドに同じ Session を使用し、成功時は1回 commit、認証・権限・検証・flush・commit 失敗時は rollback すること|
|Safe Result|成功結果に ORM Entity、Password、Password Hash を含めないこと|

---

# 9. Repository Test

本章では、Repository Layer のテストを定義する。

実際の SQLite を利用し、データアクセスを検証する。

---

## 9.1 Common Test Items

|テスト項目|内容|
|---|---|
|Find|取得|
|Create|登録|
|Update|更新|
|Delete|削除対象のみ|
|List|一覧取得|

---

## 9.2 IssueRepository

|テスト項目|内容|
|---|---|
|Find By ID|ID 検索|
|List By Project|Project 検索|
|Status Filter|Status 検索|
|Category Filter|Category 検索|
|Target Type Filter|Target Type 検索|
|Keyword Search|Description 検索|
|Combined Filters|複数検索条件の組み合わせ検索|
|Pagination|ページング|
|Sort Order|更新日時順など、定義された並び順で取得できること|

---

## 9.3 CommentRepository

|テスト項目|内容|
|---|---|
|Create|登録|
|List By Issue|Issue 検索|

---

## 9.4 AttachmentRepository

|テスト項目|内容|
|---|---|
|Create|登録|
|Delete|削除|
|Find By ID|ID 検索|
|List By Issue|Issue 検索|

---

## 9.5 Administration Persistence and Transactions

Detailed Design 11.2～11.5、11.9 の既存 Repository の追加書き込み操作と RoomTypeRepository を対象とする。実際の SQLite を利用し、Service を組み合わせた Transaction 検証も行う。同時実行では一時ファイルの SQLite DB と独立した Session / 接続を利用する。

|テスト項目|内容|
|---|---|
|Create / Update|Hotel / Project / RoomType / Room / User の登録・更新を commit 後に別 Session から取得して確認すること|
|RoomType Lookup|整数 ID で取得でき、存在しない ID では None を返すこと|
|User Counts|count_all と count_by_role が空 DB、Administrator / Engineer 混在、Role 更新後の件数を正しく返すこと|
|Password Hash|登録・変更 Password は平文保存されず、既存 verify_password で検証できること。更新省略時は Hash が変わらないこと|
|DB Constraints|username と (hotel_id, room_number) の一意制約、必須カラム、Role の CHECK 制約を維持すること|
|References|既存外部キーに従って有効な参照を保存すること。Service 経由では存在しない Hotel / RoomType、異なる Hotel の RoomType を拒否し、DB 状態を変更しないこと|
|No Repository Commit|Repository は flush までとし、呼び出し側の rollback で登録・更新を取り消せること|
|Failure Rollback|Service の検証、既存 DB 制約、flush または commit による失敗後に、新規行・変更値・updated_at が残らないこと。5対象の登録・更新を対象とすること|
|Last Administrator Rollback|拒否した Role 変更と同時指定した username / display_name / Password がすべて元の状態を維持すること|
|Concurrent Bootstrap|User が0件の DB に対する2つの bootstrap で、最大1件だけ作成されること。後続は既存 User の検証またはロック取得失敗で終了すること|
|Concurrent Demotion|Administrator が2人の状態で同時に別々の Administrator を降格しても、最低1人が残ること。認証・件数確認前に書き込み Transaction を開始すること|
|Lock Failure|書き込みロック取得失敗時は保存せず、失敗として rollback / close すること|

DB schema や Migration は変更しない。Service の参照検証と DB 自体の制約検証は区別し、外部キー制約の検証時はテスト接続で SQLite の外部キー検証を有効にする。

---

# 10. API Test

本章では REST API のテストを定義する。

FastAPI TestClient を利用する。

---

## 10.1 Authentication API

|API|テスト|
|---|---|
|Login|正常・異常 (username にメールアドレス形式を含む)・認証成功時に Session が作成されること|
|Login Failure|認証失敗時に Session が作成されず、401 Unauthorized を返すこと|
|Logout|正常・未認証・Logout 後にそれまでの Session で認証済み API を利用できないこと|
|Current User|正常・Session なし・Session に user_id なし・存在しない User ID|

---

## 10.2 Project API

|API|テスト|
|---|---|
|Project List|正常・401|

---

## 10.3 Room API

|API|テスト|
|---|---|
|Room List|正常・401・404・空一覧|

---

## 10.4 Issue API

|API|テスト|
|---|---|
|Get List|正常・401・404|
|Get Detail|正常・401・404|
|Create|正常・400・401・404|
|Update|正常・400・401・404|
|Update Status|正常・400・401・404|

---

## 10.5 AI API

|API|テスト|
|---|---|
|Generate Draft|正常・400・401・500(AI Error)|

---

## 10.6 Comment API

|API|テスト|
|---|---|
|Create|正常・400・401・404|
|List|正常・401・404|

---

## 10.7 Attachment API

|API|テスト|
|---|---|
|Upload|正常・400・401・404|
|List|正常・401・404|
|Download|正常・401・404|
|Delete|正常・401・404|

---

## 10.8 API Response Validation

すべての API について以下を確認する。

- HTTP Status
- Response Body
- Error Response
- Authentication
- Authorization
- Validation Error
- Content-Type

---

## 10.9 Speech Transcription API

`POST /api/speech/transcriptions` を対象とし、Local Speech Recognition boundary を Mock / Stub 化して検証する。

|テスト項目|内容|
|---|---|
|Transcribe Speech|認証済みユーザーが multipart/form-data の audio File を送信した場合、HTTP 200 と transcription text のみを含む `{"text": "ロビーの照明が点滅している"}` 形式のレスポンスを返すこと|
|Response Fields|Category / Description 等の AI Draft データがレスポンスに含まれないこと|
|Invalid Audio|不正な audio で 400 を返すこと。必須 audio 欠落など Service 呼び出し前の入力不正も共通エラーレスポンスの 400 とすること|
|Unauthenticated|未認証で 401 を返すこと|
|Recognition Failure|音声認識処理失敗、または利用可能な transcription text を取得できない場合に 500 を返すこと|
|No Issue Mutation|Speech API の呼び出しだけでは Issue を登録・更新しないこと（10.10参照）|

---

## 10.10 Persistence / Side Effects

Speech Transcription および AI Draft の呼び出し前後で、テスト用 SQLite の業務データを比較する。認識・生成の外部境界は Mock / Stub 化し、正常系・異常系の双方で以下を確認する。

|テスト項目|内容|
|---|---|
|Speech No Issue Mutation|Speech Transcription によって Issue が登録されず、既存 Issue の内容・更新日時も変化しないこと|
|Speech No Attachment|Speech audio 用の Attachment が登録されず、Attachment の保存処理も呼び出されないこと|
|Speech No Business Data|audio / transcription text が Issue / Attachment 等の業務データとして永続化されず、Speech 用の business data が DB に追加されないこと|
|AI Draft No Issue Mutation|AI Draft の生成だけでは Issue が登録・更新されないこと|

既存 Database Design の schema を利用し、Speech audio / transcription / AI Draft 用の Table / Column / Migration は前提としない。音声認識内部の一時ファイルの有無や削除方式はテスト条件として定義しない。ユーザーが確認した内容を既存の Issue 登録処理で保存することは、非永続化の対象外とする。

---

# 11. UI Test

本章では、画面操作に関するテストを定義する。

初期版では、UI テストは手動テストを基本とする。

---

## 11.1 Login

|テスト項目|内容|
|---|---|
|Login Success|正しいログイン ID (ユーザー名またはメールアドレス形式) とパスワードでログインできること|
|Login Success Navigation|ログイン成功後に Project Selection 画面へ遷移すること|
|Authenticated User Navigation|認証済みユーザーが Login 画面を表示した場合、Project Selection 画面へ遷移すること|
|Login Failure|誤ったログイン ID またはパスワードでログインできないこと|
|Required Fields|必須項目が未入力の場合、エラーが表示されること|

---

## 11.2 Project Selection

|テスト項目|内容|
|---|---|
|Project List|Project 一覧が表示されること|
|Select Project|Project 選択後に Issue List へ遷移すること|
|Selected Project Storage|選択した Project の識別情報が `sessionStorage` に保存されること|
|Selected Project Retention|選択した Project が同一ブラウザセッション中の画面遷移で維持されること|
|Unauthenticated Access|未認証または Session 期限切れの場合、Login 画面へ遷移すること|
|Logout|Logout 後に `sessionStorage` に保存した Project の識別情報が削除されること|

---

## 11.3 Issue List

|テスト項目|内容|
|---|---|
|List Display|Issue 一覧が表示されること|
|Initial Search Conditions|初期表示時は検索条件が指定されず、選択中 Project の Issue 一覧が表示されること|
|All Options|Status、Category および Target Type に `All` が表示されること|
|Search|検索条件で絞り込みできること|
|Search Page Reset|検索実行時に1ページ目が表示されること|
|Pagination|Previous Page および Next Page でページ移動できること|
|Pagination Boundary|前後のページが存在しない場合、対応するページ移動操作が無効になること|
|Page Size|1ページあたりの表示件数が20件であること|
|Open Detail|Issue Detail 画面へ遷移すること|
|New Issue|Issue Create 画面へ遷移すること|
|No Selected Project|Project が選択されていない場合、Project Selection 画面へ遷移すること|
|Authentication Failure|認証が必要な API から `401 Unauthorized` が返却された場合、Login 画面へ遷移すること|

---

## 11.4 Issue Detail

|テスト項目|内容|
|---|---|
|Detail Display|Issue 情報が表示されること|
|Comment Display|Comment 一覧が表示されること|
|Attachment Display|Attachment 一覧が表示されること|
|Edit|Issue Edit 画面へ遷移すること|
|Add Comment|Comment を追加できること|
|Upload Attachment|Attachment を追加できること|
|Open Attachment|添付ファイルを表示できること|
|Back|Issue List へ戻ること|
|Invalid Issue ID|Issue ID が指定されていない、または不正な場合、Issue List 画面へ遷移すること|
|Issue Not Found|存在しない Issue の場合、Issue List 画面へ遷移すること|
|Authentication Failure|認証が必要な API から `401 Unauthorized` が返却された場合、Login 画面へ遷移すること|

---

## 11.5 Issue Create

Input Assistance は Requirements v1.3 §7.12、UI Design §12.7、Detailed Design §6.3 に従って確認する。

|テスト項目|内容|
|---|---|
|Create Issue|Issue を登録できること|
|Required Fields|Target Type、Category、Description が未入力の場合にエラーが表示されること|
|ROOM Validation|Target Type = ROOM の場合、Room 未選択でエラーとなること|
|OTHER Validation|Target Type = OTHER の場合、Target 未入力でエラーとなること|
|AI Draft|Voice / Text Input のテキストから Category と日本語 Description を生成できること|
|Voice Input|Voice Input から audio を POST /api/speech/transcriptions に送信できること|
|Transcription Display|返却された transcription text が既存の Voice / Text Input に表示されること|
|Transcription Edit|同じ入力欄で transcription text をユーザーが編集できること|
|No Mandatory Transcription Confirmation|独立した必須確認画面・必須確認操作を要求せず、修正しない場合も Generate AI Draft を実行できること|
|Generate Edited Draft|ユーザーの Generate AI Draft 操作で、編集後の Voice / Text Input のテキストを input_text として POST /api/ai/issue-draft に送信すること。raw audio を渡さないこと|
|Direct Text Input|テキスト直接入力では Speech Transcription を呼び出さず AI Draft を生成できること|
|Speech Processing|Speech Recognition の処理中表示を確認すること|
|Separate Errors|Speech Recognition Error と AI Draft Error を区別して表示すること|
|User in Control|AI Draft の Category / Description を確認し、必要に応じて修正してから Save で Issue を登録できること。音声認識・AI Draft 生成だけでは登録されないこと|
|Target Unchanged|ユーザーが指定した Target Type / Room / Target を AI が推定・変更しないこと|
|Save Previous Values|登録成功時に、その Issue に使用した Target Type、Room、Category が対象 Project の前回利用値として localStorage に保存されること|
|Restore Previous Values|Issue Create を開いたとき、現在選択中の Project の前回利用値が初期表示され、別 Project の保存値は使用されないこと|
|Restore Available Room|保存された Room が現在の Project で選択可能な場合だけ復元され、選択できない Room や別 Project の Room は復元されないこと|
|Missing or Invalid Values|保存値が存在しない、無効、または現在利用できない項目は復元されず、その項目が通常の初期状態となること|
|Save OTHER Target History|OTHER の登録成功時だけ、その Target が対象 Project の localStorage の履歴へ追加されること。ROOM の登録では追加されないこと|
|OTHER Target Candidates|OTHER の場合に現在の Project の履歴だけが候補表示され、ユーザーが候補を選択できること。ROOM の場合は候補表示されないこと|
|Free Target Input|履歴候補を使用せず自由入力でき、AI が Target を推測・自動決定しないこと|
|No Save Before Success|登録失敗、入力中、キャンセル、AI Draft 生成では前回利用値および Target 履歴が更新されないこと|
|localStorage Read Failure|localStorage が利用できない場合や保存データを解析できない場合、入力支援の値・履歴を適用せず通常の入力・Issue 登録を継続できること|
|localStorage Write Failure|登録成功後に localStorage の保存が失敗しても、Issue 登録は成功として扱われること|

---

## 11.6 Issue Edit

|テスト項目|内容|
|---|---|
|Update Issue|Issue を更新できること|
|Update Status|Status を変更できること|
|Preserve Current Values|localStorage に前回利用値が存在しても編集対象 Issue の現在値が初期表示され、上書きされないこと|
|No Input Assistance Update|Issue Edit の更新成功時も、前回利用値および OTHER Target 履歴が更新されないこと|
|Required Fields|Target Type、Category、Description が未入力の場合にエラーが表示されること|
|ROOM Validation|Target Type = ROOM の場合、Room 未選択でエラーとなること|
|OTHER Validation|Target Type = OTHER の場合、Target 未入力でエラーとなること|

---

# 12. AI Test

本章では、AI Draft 機能のテストを定義する。

6.1 の Ollama または Mock を利用する方針を維持し、Service 自動テストでは Ollama を Mock 化する。日本語 Description は、Prompt に日本語生成の指示があることと、日本語の Mock 応答が返却・表示されることを確認する。実モデルの品質・精度・性能に新たな合否基準は設けない。

---

## 12.1 Normal Case

|テスト項目|内容|
|---|---|
|Generate Draft|AI Draft が生成されること|
|Description|Description が日本語で生成されること|
|Text Input|AIService が Voice / Text Input のテキスト（必要に応じて修正した文字起こし結果、または直接入力したテキスト）を受け取ること|
|No Speech Processing|AIService に raw audio を渡さず、AIService が Local Speech Recognition を呼び出さないこと|
|Output Only|生成結果が Category と Description のみであること|
|Target Unchanged|Target Type / Room / Target を推定・変更しないこと|
|Category|Category が生成されること|
|Target Type Not Returned|Target Type がレスポンスに含まれないこと|
|Room Not Returned|Room がレスポンスに含まれないこと|
|Target Not Returned|Target がレスポンスに含まれないこと|
|Unknown Category|Category を判定できない場合に OTHER が返却されること|

---

## 12.2 Error Case

|テスト項目|内容|
|---|---|
|Empty Input|空入力でエラーとなること|
|Ollama Error|AIエラー時に適切なメッセージを表示すること|
|Invalid Response|不正なレスポンスを処理できること|

---

## 12.3 User Confirmation

AI Draft の生成だけでは Issue を登録・更新せず、ユーザーが Category / 日本語 Description を確認し、必要に応じて修正した後、Save により Issue を登録できることを確認する（10.10、11.5参照）。

---

# 13. File Upload Test

本章では、Attachment 機能のテストを定義する。

---

## 13.1 Upload

|テスト項目|内容|
|---|---|
|JPEG Upload|JPEG 画像をアップロードできること|
|PNG Upload|PNG 画像をアップロードできること|
|MP4 Upload|MP4 動画をアップロードできること|
|QuickTime Upload|QuickTime 動画をアップロードできること|
|Multiple Uploads|同一 Issue に複数の Attachment を登録できること|
|Issue Not Found|存在しない Issue へのアップロードでエラーとなること|
|User Not Found|存在しない User によるアップロードでエラーとなること|
|Invalid File Name|元ファイル名が欠落、空文字、パス形式、または制御文字を含む場合にエラーとなること|
|Invalid MIME Type|許可されていない MIME Type を拒否すること|
|Invalid Extension|許可されていない拡張子を拒否すること|
|MIME Type and Extension Mismatch|MIME Type と拡張子の組み合わせが不正な場合にエラーとなること|
|Image Size Limit|画像は 10 MiB 以下を許可し、10 MiB を超える場合にエラーとなること|
|Video Size Limit|動画は 100 MiB 以下を許可し、100 MiB を超える場合にエラーとなること|
|Empty File|0 byte のファイルを拒否すること|
|Generated File Name|保存用ファイル名が UUID v4 と元ファイルの拡張子から生成されること|
|Unique File Name|同じ元ファイル名を複数回アップロードしても保存用ファイル名が衝突しないこと|
|Relative File Path|DB に Storage Root からの相対パスが保存されること|
|Metadata Registration|ファイル情報が DB に登録されること|
|Storage Save|ファイル本体が Local Storage に保存されること|

---

## 13.2 Download

|テスト項目|内容|
|---|---|
|Download|添付ファイル本体を取得できること|
|Content Type|登録された MIME Type でファイルが返却されること|
|Unauthorized|未認証ユーザーは 401 Unauthorized を返すこと|
|Not Found|存在しない Attachment で 404 となること|
|Storage File Not Found|DB 情報は存在するが Local Storage にファイルが存在しない場合にエラーとなること|

---

## 13.3 Delete

|テスト項目|内容|
|---|---|
|Delete Attachment|添付ファイルを削除できること|
|Delete Staging|物理ファイルが Storage Root 配下の `.trash/` へ一時退避されること|
|Metadata Delete|一時退避後に DB の Attachment 情報が削除されること|
|Storage Delete|DB commit 成功後に `.trash/` の物理ファイルが削除されること|
|Issue Not Found|存在しない Issue を指定した場合にエラーとなること|
|Attachment Not Found|存在しない Attachment を指定した場合にエラーとなること|
|Already Deleted Attachment|既に削除済みの Attachment を指定した場合にエラーとなること|
|Attachment and Issue Mismatch|指定した Attachment が別の Issue に属する場合にエラーとなること|
|User Not Found|存在しない User による削除でエラーとなること|
|Storage File Not Found|DB 情報は存在するが物理ファイルが存在しない場合、物理ファイルは既に削除済みとみなし、DB の Attachment 情報の削除を継続すること|

---

## 13.4 Failure and Consistency

|テスト項目|内容|
|---|---|
|Storage Save Failure|Local Storage への保存に失敗した場合、Attachment 情報が DB に登録されないこと|
|Metadata Registration Failure|DB 登録または commit に失敗した場合、DB を rollback し、保存済みファイルを補償削除すること|
|Upload Compensation Failure|DB 登録または commit 失敗後の補償削除にも失敗した場合、StorageError とし、元の DB 例外より補償削除の失敗を優先して外部へ報告すること。孤立ファイルが残る可能性を許容すること|
|Delete Staging Failure|物理ファイルの `.trash/` への一時退避に失敗した場合、DB の Attachment 情報を削除しないこと|
|Metadata Delete Failure|`.trash/` への一時退避後に DB 削除または commit が失敗した場合、DB を rollback し、物理ファイルを元の場所へ復元すること|
|Delete Restore Failure|DB rollback 後の物理ファイル復元にも失敗した場合、元の DB 例外を優先し、残存状態をエラーとして扱うこと|
|Trash Delete Failure|DB commit 成功後に `.trash/` の物理ファイル削除に失敗した場合、DB 削除は成功扱いとし、`.trash/` に孤立ファイルが残ることを許容すること|
|Consistency|通常の単一障害では DB metadata と物理ファイルの整合性を維持し、補償処理自体も失敗する二重障害では最新 Detailed Design で定義された残存状態を許容すること|

---

# 14. Error Handling Test

本章では、エラー処理のテストを定義する。

---

## 14.1 Validation Error

以下を確認する。

- 必須項目
- Target Type
- Target
- Category
- Status
- Room
- Project
- Description

---

## 14.2 Authentication Error

以下を確認する。

- Username が存在しない場合に `401 Unauthorized` を返すこと。
- Password が一致しない場合に `401 Unauthorized` を返すこと。
- Username 不存在と Password 不一致で、外部へ返す認証エラー内容から Username の存在有無を判別できないこと。
- Session が存在しない場合に `401 Unauthorized` を返すこと。
- Session に `user_id` が存在しない場合に `401 Unauthorized` を返すこと。
- Session の `user_id` に対応する User が存在しない場合に `401 Unauthorized` を返すこと。
- Logout 後、それまでの Session で認証が必要な API へアクセスした場合に `401 Unauthorized` を返すこと。

---

## 14.3 Authorization Error

以下を確認する。

- 権限不足
- Administrator 専用機能へのアクセス

---

## 14.4 System Error

以下を確認する。

- Database Error
- AIServiceError
- StorageError
- Unexpected Exception

ユーザーには共通エラーメッセージを返し、詳細情報はログへ記録する。

---

## 14.5 Not Found Error

以下を確認する。

- Project が存在しない
- Room が存在しない
- Issue が存在しない
- Attachment が存在しない

---

## 14.6 Business Rule Error

以下を確認する。

- ROOM に Target を指定した場合
- OTHER に Room を指定した場合
- Room と Project が異なる Hotel に属する場合

---

## 14.7 Speech Transcription Error

|テスト項目|例外|HTTP Status|
|---|---|---|
|Invalid Audio|ValidationError|400|
|Unauthenticated|AuthenticationError|401|
|Speech Recognition Failure|SpeechRecognitionError|500|

利用可能な transcription text を取得できない場合も SpeechRecognitionError とする。共通エラーレスポンス形式に従い、Speech Recognition Error と AI Draft Error（AIServiceError）を別のエラーとして扱い、画面上でも区別することを確認する。具体的な製品固有の例外はテスト仕様に持ち込まない。

---

# 15. Authorization Test

本章では、認可に関するテストを定義する。

Speech Transcription は認証を必要とし、ENGINEER / ADMINISTRATOR の双方が利用できることを確認する。

---

## 15.1 Administrator

以下を確認する。

- Project Selection / Project API
- Issue Management
- Speech Transcription
- AI Draft
- Comment
- Attachment
- Administration

---

## 15.2 Engineer

以下を確認する。

- Project Selection / Project API
- Issue Management
- Speech Transcription
- AI Draft
- Comment
- Attachment
- Administration を利用できないこと

---

## 15.3 Unauthorized Access

以下を確認する。

- 未認証ユーザーは 401 Unauthorized を返すこと
- 権限不足ユーザーは 403 Forbidden を返すこと

---

## 15.4 Administration CLI

Detailed Design 10.11 に従う。引数解析・表示・終了コードは CLI entry point の自動テストで検証し、`getpass` は Mock 化する。永続化を含む代表的な実行は専用 SQLite と擬似端末付き subprocess を利用し、`backend/` から `uv run python -m app.cli ...` で検証する。端末の非表示入力は実装後に手動で確認する。

|テスト項目|内容|
|---|---|
|Command Coverage|hotel / project / room-type / room / user の create / update と user bootstrap-admin を実行できること|
|Integer IDs|更新対象 ID と参照 ID は整数で解析し、非整数では終了コード2となること|
|Required Arguments|必須引数不足、不明なコマンド / 引数、不正な Role は終了コード2となり、Password 入力と DB 書き込みを行わないこと|
|Unsupported Operations|CSV、delete、所属 Hotel の更新、bootstrap の Role 指定、コマンドライン Password 指定を受け付けないこと|
|Administrator Credentials|通常操作は --admin-username が必須で、毎回 getpass で認証 Password を入力すること。CLI 内に認証状態を保存しないこと|
|New Password|User create / bootstrap / --set-password では認証用と区別した非表示プロンプトを使用し、User update で省略時は新しい Password を要求しないこと|
|Hidden Input Failure|getpass の非表示入力が利用できない場合、入力中断・EOF の場合は終了コード1とし、表示入力へ fallback せず DB を変更しないこと|
|Success Exit|commit 成功後だけ対象と整数 ID を stdout に表示し、終了コード0となること|
|Failure Exit|認証・権限・Service 検証・bootstrap 禁止・最後の Administrator 保護・DB / ロック処理失敗は stderr に安全なメッセージを表示し、終了コード1となること|
|Help|--help は終了コード0となり、認証・DB 書き込みを行わないこと|
|Safe Output|stdout / stderr / ログに Password、Password Hash、DB 接続情報、SQL、パラメーター、traceback を出さないこと。DB 例外の生文字列を表示しないこと|
|Authentication Message|username 不存在と Password 不一致で同じ安全なメッセージを表示すること|
|Session Cleanup|成功・失敗の双方で Session を close し、失敗時に成功メッセージを表示しないこと|

CLI の失敗に HTTP status は適用しない。15.3 の401 / 403は既存 HTTP API の検証とし、Administration CLI は上記終了コードで検証する。

---

# 16. Future Enhancements

将来的に以下のテストを追加する。

- E2E Test (Playwright)
- Contract Test (OpenAPI)
- Performance Test
- Load Test
- Security Test
- Accessibility Test
- Cross Browser Test
- CI/CD による自動テスト
- Docker 環境での自動テスト

これらは初期版のテスト範囲には含めない。

---

# End of Document
