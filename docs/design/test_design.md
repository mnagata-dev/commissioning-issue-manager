# CIM Test Design

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

本書は、CIM（Commissioning Issue Manager）のテスト設計を定義することを目的とする。

本書では、テスト方針、テストレベル、テスト観点、および主要機能ごとのテスト内容を定義する。

本書を基に、pytestおよび手動テストを実施する。

---

# 2. Scope

本書では以下を対象とする。

* Unit Test
* Service Test
* Repository Test
* API Test
* UI Test
* AI Test
* File Upload Test
* Error Handling Test
* Authorization Test

以下は対象外とする。

* 本番運用監視
* 負荷試験の詳細
* セキュリティ診断の詳細
* クラウド環境での試験

これらは将来必要になった時点で別途定義する。

---

# 3. References

本書は以下のドキュメントを参照する。

| ドキュメント                 | 説明          |
| ---------------------- | ----------- |
| requirements.md        | 要件定義書       |
| basic_design.md        | 基本設計書       |
| database_design.md     | データベース設計書   |
| api_design.md          | API設計書      |
| ui_design.md           | UI設計書       |
| detailed_design.md     | 詳細設計書       |
| project_conventions.md | プロジェクト共通ルール |

---

# 4. Test Policy

## 4.1 Basic Policy

CIMでは、Service LayerとAPIを中心にテストする。

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

* Service Test
* Repository Test
* API Test
* Validation Test

UIの詳細操作は初期版では手動テストを中心とする。

---

# 5. Test Levels

本システムでは以下のテストレベルを採用する。

| テストレベル          | 説明               |
| --------------- | ---------------- |
| Unit Test       | 小さな関数・メソッド単位のテスト |
| Service Test    | 業務ロジックのテスト       |
| Repository Test | DBアクセスのテスト       |
| API Test        | REST APIのテスト     |
| UI Test         | 画面操作の確認          |
| Manual Test     | 実利用に近い確認         |

---

# 6. Test Environment

## 6.1 Development Test Environment

| 項目             | 内容                           |
| -------------- | ---------------------------- |
| OS             | Windows 11 + WSL2 Ubuntu LTS |
| Backend        | FastAPI                      |
| Database       | SQLite                       |
| Test Framework | pytest                       |
| API Test       | FastAPI TestClient           |
| AI             | Ollama または Mock              |
| File Storage   | Local Storage                |

---

## 6.2 Test Database

テストでは本番用DBとは別のSQLite DBを利用する。

テストごとにデータを初期化できる構成とする。

---

## 6.3 Test File Storage

Attachmentテストでは、テスト専用の一時ディレクトリを利用する。

テスト終了後、作成ファイルを削除する。

---

# 7. Unit Test

本章では、単体テスト（Unit Test）の方針を定義する。

---

## 7.1 Purpose

小さな関数・ユーティリティ・バリデーション処理が期待どおり動作することを確認する。

---

## 7.2 Target

| 対象                   | 内容                            |
| -------------------- | ----------------------------- |
| Utility Functions    | 共通関数                          |
| Validation Functions | 入力値検証                         |
| File Name Generator  | 保存ファイル名生成                     |
| Path Generator       | 保存パス生成                        |
| Enum Conversion      | TargetType、Category、Statusの変換 |

---

## 7.3 Test Items

| テスト項目          | 内容   |
| -------------- | ---- |
| Normal Case    | 正常入力 |
| Boundary Value | 境界値  |
| Invalid Value  | 不正入力 |
| Null           | 未入力  |
| Exception      | 例外発生 |

---

# 8. Service Test

本章では、Service Layerのテストを定義する。

RepositoryはMock化し、業務ロジックのみを検証する。

---

## 8.1 AuthService

| テスト項目         | 内容         |
| ------------- | ---------- |
| Login Success | 正常ログイン     |
| Login Failure | 認証失敗       |
| Current User  | ログインユーザー取得 |

---

## 8.2 ProjectService

| テスト項目             | 内容           |
| ----------------- | ------------ |
| Project List      | Project一覧取得  |
| Project Not Found | 存在しないProject |

---

## 8.3 IssueService

| テスト項目              | 内容           |
| ------------------ | ------------ |
| Create Issue       | 正常登録         |
| Update Issue       | 正常更新         |
| Change Status      | Status変更     |
| Get Detail         | 詳細取得         |
| List Issues        | 一覧取得         |
| Invalid TargetType | 不正TargetType |
| Invalid Category   | 不正Category   |
| Invalid Status     | 不正Status     |
| Room Not Found     | Room不存在      |
| Project Not Found  | Project不存在   |

---

## 8.4 AIService

| テスト項目            | 内容        |
| ---------------- | --------- |
| Generate Draft   | 正常生成      |
| Empty Input      | 空入力       |
| Ollama Error     | AI呼び出し失敗  |
| Invalid Response | AIレスポンス不正 |

---

## 8.5 CommentService

| テスト項目           | 内容       |
| --------------- | -------- |
| Add Comment     | 正常登録     |
| Empty Comment   | 空コメント    |
| Issue Not Found | Issue不存在 |

---

## 8.6 AttachmentService

| テスト項目             | 内容    |
| ----------------- | ----- |
| Upload Image      | 画像登録  |
| Upload Video      | 動画登録  |
| Delete Attachment | 削除    |
| Invalid Extension | 不正拡張子 |
| Large File        | サイズ超過 |

---

# 9. Repository Test

本章では、Repository Layerのテストを定義する。

実際のSQLiteを利用し、データアクセスを検証する。

---

## 9.1 Common Test Items

| テスト項目  | 内容     |
| ------ | ------ |
| Find   | 取得     |
| Create | 登録     |
| Update | 更新     |
| Delete | 削除対象のみ |
| List   | 一覧取得   |

---

## 9.2 IssueRepository

| テスト項目             | 内容            |
| ----------------- | ------------- |
| Find By ID        | ID検索          |
| List By Project   | Project検索     |
| Status Filter     | Status検索      |
| Category Filter   | Category検索    |
| TargetType Filter | TargetType検索  |
| Keyword Search    | Description検索 |
| Pagination        | ページング         |

---

## 9.3 CommentRepository

| テスト項目         | 内容      |
| ------------- | ------- |
| Create        | 登録      |
| List By Issue | Issue検索 |

---

## 9.4 AttachmentRepository

| テスト項目         | 内容      |
| ------------- | ------- |
| Create        | 登録      |
| Delete        | 削除      |
| Find By ID    | ID検索    |
| List By Issue | Issue検索 |

---

# 10. API Test

本章ではREST APIのテストを定義する。

FastAPI TestClientを利用する。

---

## 10.1 Authentication API

| API          | テスト    |
| ------------ | ------ |
| Login        | 正常・異常  |
| Logout       | 正常     |
| Current User | 正常・未認証 |

---

## 10.2 Project API

| API          | テスト  |
| ------------ | ---- |
| Project List | 正常取得 |

---

## 10.3 Issue API

| API           | テスト           |
| ------------- | ------------- |
| Get List      | 正常            |
| Get Detail    | 正常・404        |
| Create        | 正常・Validation |
| Update        | 正常・Validation |
| Update Status | 正常・Validation |

---

## 10.4 AI API

| API            | テスト   |
| -------------- | ----- |
| Generate Draft | 正常・異常 |

---

## 10.5 Comment API

| API    | テスト           |
| ------ | ------------- |
| Create | 正常・Validation |
| List   | 正常            |

---

## 10.6 Attachment API

| API      | テスト    |
| -------- | ------ |
| Upload   | 正常・異常  |
| Download | 正常・404 |
| Delete   | 正常・404 |

---

## 10.7 API Response Validation

すべてのAPIについて以下を確認する。

* HTTP Status
* Response JSON
* Error Response
* 認証
* 認可
* Validation Error
* Content-Type

---

# 11. UI Test

本章では、画面操作に関するテストを定義する。

初期版では、UIテストは手動テストを基本とする。

---

## 11.1 Login

| テスト項目           | 内容                      |
| --------------- | ----------------------- |
| Login Success   | 正しい認証情報でログインできること       |
| Login Failure   | 誤った認証情報でログインできないこと      |
| Required Fields | 必須項目が未入力の場合、エラーが表示されること |

---

## 11.2 Project Selection

| テスト項目          | 内容                           |
| -------------- | ---------------------------- |
| Project List   | Project一覧が表示されること            |
| Select Project | Project選択後にIssue Listへ遷移すること |

---

## 11.3 Issue List

| テスト項目        | 内容                  |
| ------------ | ------------------- |
| List Display | Issue一覧が表示されること     |
| Search       | 検索条件で絞り込みできること      |
| Open Detail  | Issue Detailへ遷移すること |
| New Issue    | Issue Createへ遷移すること |

---

## 11.4 Issue Detail

| テスト項目              | 内容                   |
| ------------------ | -------------------- |
| Detail Display     | Issue情報が表示されること      |
| Comment Display    | Comment一覧が表示されること    |
| Attachment Display | Attachment一覧が表示されること |

---

## 11.5 Issue Create

| テスト項目        | 内容                   |
| ------------ | -------------------- |
| Create Issue | Issueを登録できること        |
| Validation   | 必須項目未入力時にエラーが表示されること |
| AI Draft     | AI Draftを生成できること     |

---

## 11.6 Issue Edit

| テスト項目         | 内容             |
| ------------- | -------------- |
| Update Issue  | Issueを更新できること  |
| Update Status | Statusを変更できること |
| Validation    | 入力エラーが表示されること  |

---

# 12. AI Test

本章では、AI Draft機能のテストを定義する。

---

## 12.1 Normal Case

| テスト項目          | 内容                  |
| -------------- | ------------------- |
| Generate Draft | AI Draftが生成されること    |
| Description    | Descriptionが生成されること |
| TargetType     | TargetTypeが推定されること  |
| Category       | Categoryが推定されること    |

---

## 12.2 Error Case

| テスト項目            | 内容                     |
| ---------------- | ---------------------- |
| Empty Input      | 空入力でエラーとなること           |
| Ollama Error     | AIエラー時に適切なメッセージを表示すること |
| Invalid Response | 不正なレスポンスを処理できること       |

---

## 12.3 User Confirmation

AI Draftは保存されず、利用者が確認・修正した後にIssueを登録できることを確認する。

---

# 13. File Upload Test

本章では、Attachment機能のテストを定義する。

---

## 13.1 Upload

| テスト項目        | 内容               |
| ------------ | ---------------- |
| Image Upload | 画像をアップロードできること   |
| Video Upload | 動画をアップロードできること   |
| Invalid File | 不正なファイル形式を拒否すること |
| Large File   | サイズ超過時にエラーとなること  |

---

## 13.2 Download

| テスト項目     | 内容                       |
| --------- | ------------------------ |
| Download  | 添付ファイルを取得できること           |
| Not Found | 存在しないAttachmentで404となること |

---

## 13.3 Delete

| テスト項目             | 内容                         |
| ----------------- | -------------------------- |
| Delete Attachment | 添付ファイルを削除できること             |
| Storage Delete    | Local Storageのファイルも削除されること |
| Metadata Delete   | DBの管理情報も削除されること            |

---

# 14. Error Handling Test

本章では、エラー処理のテストを定義する。

---

## 14.1 Validation Error

以下を確認する。

* 必須項目
* TargetType
* Category
* Status
* Room
* Project

---

## 14.2 Authentication Error

以下を確認する。

* 未認証
* 不正認証情報

---

## 14.3 Authorization Error

以下を確認する。

* 権限不足
* Administrator専用機能へのアクセス

---

## 14.4 System Error

以下を確認する。

* DBエラー
* AIエラー
* File Storageエラー

利用者には共通エラーメッセージを返し、詳細情報はログへ記録する。

---

# 15. Authorization Test

本章では、認可に関するテストを定義する。

---

## 15.1 Administrator

Administratorが利用可能な機能を利用できることを確認する。

---

## 15.2 Engineer

Engineerが以下を利用できることを確認する。

* Project Selection
* Issue Management
* AI Draft
* Comment
* Attachment

Administrator専用機能は利用できないことを確認する。

---

## 15.3 Unauthorized Access

未認証利用者が保護されたAPIへアクセスできないことを確認する。

---

# 16. Future Enhancements

将来的に以下のテストを追加する。

* E2E Test（Playwright）
* Performance Test
* Load Test
* Security Test
* Accessibility Test
* Cross Browser Test
* CI/CDによる自動テスト
* Docker環境での自動テスト

これらは初期版のテスト範囲には含めない。

---

# End of Document
