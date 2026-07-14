# CIM Test Design

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-14
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Update authentication and master data related test cases.|
|1.2|2026-07-14|Align test design with Requirements v1.2, API Design, UI Design, and Detailed Design. Add validation, AI Draft, attachment, and business rule test cases.|

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
- File Upload Test
- Error Handling Test
- Authorization Test

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

---

# 4. Test Policy

## 4.1 Basic Policy

CIM では、Service Layer と API を中心にテストする。

初期版では、自動テストと手動テストを併用する。

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
- username にメールアドレス形式を利用できること

UI の詳細操作は初期版では手動テストを中心とする。

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

## 8.3 IssueService

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
|Room and Project Mismatch|Room と Project が異なる Hotel に属する|
|Invalid Category|不正な Category|
|Invalid Status|不正な Status|
|Room Not Found|存在しない Room|
|Project Not Found|存在しない Project|

---

## 8.4 AIService

|テスト項目|内容|
|---|---|
|Generate Draft|正常生成|
|Empty Input|空入力|
|Ollama Error|AI 呼び出し失敗|
|Invalid Response|AI レスポンス不正|
|Target Information Ignored|AI が Target Type・Room・Target を返却しないこと|
|Unknown Category|Category を判定できない場合に OTHER を返却すること|

---

## 8.5 CommentService

|テスト項目|内容|
|---|---|
|Add Comment|正常登録|
|Empty Comment|空コメント|
|Issue Not Found|Issue 不存在|

---

## 8.6 AttachmentService

|テスト項目|内容|
|---|---|
|Upload Image|画像登録|
|Upload Video|動画登録|
|Delete Attachment|削除|
|Invalid Extension|不正拡張子|
|Large File|サイズ超過|

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

# 10. API Test

本章では REST API のテストを定義する。

FastAPI TestClient を利用する。

---

## 10.1 Authentication API

|API|テスト|
|---|---|
|Login|正常・異常 (username にメールアドレス形式を含む)|
|Logout|正常|
|Current User|正常・未認証|

---

## 10.2 Project API

|API|テスト|
|---|---|
|Project List|正常・401|

---

## 10.3 Issue API

|API|テスト|
|---|---|
|Get List|正常・401・404|
|Get Detail|正常・401・404|
|Create|正常・400・401・404|
|Update|正常・400・401・404|
|Update Status|正常・400・401・404|

---

## 10.4 AI API

|API|テスト|
|---|---|
|Generate Draft|正常・400・401・500(AI Error)|

---

## 10.5 Comment API

|API|テスト|
|---|---|
|Create|正常・400・401・404|
|List|正常・401・404|

---

## 10.6 Attachment API

|API|テスト|
|---|---|
|Upload|正常・400・401・404|
|List|正常・401・404|
|Download|正常・401・404|
|Delete|正常・401・404|

---

## 10.7 API Response Validation

すべての API について以下を確認する。

- HTTP Status
- Response Body
- Error Response
- Authentication
- Authorization
- Validation Error
- Content-Type

---

# 11. UI Test

本章では、画面操作に関するテストを定義する。

初期版では、UI テストは手動テストを基本とする。

---

## 11.1 Login

|テスト項目|内容|
|---|---|
|Login Success|正しいログイン ID (ユーザー名またはメールアドレス形式) とパスワードでログインできること|
|Login Failure|誤ったログイン ID またはパスワードでログインできないこと|
|Required Fields|必須項目が未入力の場合、エラーが表示されること|

---

## 11.2 Project Selection

|テスト項目|内容|
|---|---|
|Project List|Project 一覧が表示されること|
|Select Project|Project 選択後に Issue List へ遷移すること|

---

## 11.3 Issue List

|テスト項目|内容|
|---|---|
|List Display|Issue 一覧が表示されること|
|Search|検索条件で絞り込みできること|
|Open Detail|Issue Detail へ遷移すること|
|New Issue|Issue Create へ遷移すること|

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

---

## 11.5 Issue Create

|テスト項目|内容|
|---|---|
|Create Issue|Issue を登録できること|
|Required Fields|Target Type、Category、Description が未入力の場合にエラーが表示されること|
|ROOM Validation|Target Type = ROOM の場合、Room 未選択でエラーとなること|
|OTHER Validation|Target Type = OTHER の場合、Target 未入力でエラーとなること|
|AI Draft|AI Draft を生成できること|

---

## 11.6 Issue Edit

|テスト項目|内容|
|---|---|
|Update Issue|Issue を更新できること|
|Update Status|Status を変更できること|
|Required Fields|Target Type、Category、Description が未入力の場合にエラーが表示されること|
|ROOM Validation|Target Type = ROOM の場合、Room 未選択でエラーとなること|
|OTHER Validation|Target Type = OTHER の場合、Target 未入力でエラーとなること|

---

# 12. AI Test

本章では、AI Draft 機能のテストを定義する。

---

## 12.1 Normal Case

|テスト項目|内容|
|---|---|
|Generate Draft|AI Draft が生成されること|
|Description|Description が生成されること|
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

AI Draft は保存されず、ユーザーが確認・修正した後に Issue を登録できることを確認する。

---

# 13. File Upload Test

本章では、Attachment 機能のテストを定義する。

---

## 13.1 Upload

|テスト項目|内容|
|---|---|
|Image Upload|画像をアップロードできること|
|Video Upload|動画をアップロードできること|
|Multiple Uploads|同一 Issue に複数の Attachment を登録できること|
|Issue Not Found|存在しない Issue へのアップロードでエラーとなること|
|Invalid File|不正なファイル形式を拒否すること|
|Large File|サイズ超過時にエラーとなること|
|Empty File|空ファイルを拒否すること|
|Generated File Name|保存用ファイル名が生成されること|
|Relative File Path|DB に相対パスが保存されること|
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
|Storage Delete|Local Storage のファイルも削除されること|
|Metadata Delete|DB の管理情報も削除されること|
|Issue Not Found|存在しない Issue を指定した場合にエラーとなること|
|Attachment Not Found|存在しない Attachment を指定した場合にエラーとなること|
|Already Deleted Attachment|既に削除済みの Attachment を指定した場合にエラーとなること|
|Attachment and Issue Mismatch|指定した Attachment が別の Issue に属する場合にエラーとなること|

---

## 13.4 Failure and Consistency

|テスト項目|内容|
|---|---|
|Storage Save Failure|Local Storage への保存に失敗した場合、Attachment 情報が DB に登録されないこと|
|Metadata Registration Failure|DB 登録に失敗した場合、保存済みファイルが Local Storage に残らないこと|
|Storage Delete Failure|Local Storage の削除に失敗した場合、Attachment 情報の削除が完了扱いにならないこと|
|No Partial State|処理失敗時にファイルまたは DB 情報だけが残らないこと|

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

- 未認証
- 不正認証情報

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

# 15. Authorization Test

本章では、認可に関するテストを定義する。

---

## 15.1 Administrator

以下を確認する。

- Project Selection / Project API
- Issue Management
- AI Draft
- Comment
- Attachment
- Administration

---

## 15.2 Engineer

以下を確認する。

- Project Selection / Project API
- Issue Management
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
