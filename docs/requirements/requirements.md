# CIM Requirements Specification

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
3. Background
4. Goals
5. Users
6. System Overview
7. Functional Requirements
8. Non-functional Requirements
9. Data Requirements
10. AI Requirements
11. Operational Requirements
12. Constraints
13. Future Enhancements
14. Glossary

---

# 1. Purpose

本書は、CIM（Commissioning Issue Manager）の要件を定義することを目的とする。

本書では、本システムが満たすべき機能要件、非機能要件、データ要件、AI要件、および運用要件を定義する。

本書を基に、基本設計、詳細設計、実装およびテストを実施する。

---

# 2. Scope

本書では以下を対象とする。

* システムの目的
* 利用者
* システム概要
* 機能要件
* 非機能要件
* データ要件
* AI要件
* 運用要件
* システム制約
* 将来拡張

以下は本書の対象外とする。

* データベース設計
* API設計
* UI設計
* クラス設計
* テスト設計

これらは各設計書で定義する。

---

# 3. Background

Lutronシステムのコミッショニングでは、多数のIssueが発生する。

現場ではMicrosoft TeamsやExcelなどを利用してIssueを管理することが多く、以下の課題が存在する。

* Issue管理が属人的になりやすい。
* 音声メモからIssueを整理する作業に時間を要する。
* 写真・動画とIssueの関連付けが煩雑である。
* Room、RoomType、Area単位でIssueを整理しづらい。
* Project全体の進捗や未解決Issueを把握しづらい。

これらの課題を解決するため、コミッショニング業務に特化したIssue管理システムとしてCIMを開発する。

---

# 4. Goals

本システムの目的を以下に示す。

## 4.1 Issue管理の効率化

コミッショニング時に発生するIssueを迅速かつ正確に登録・管理できること。

---

## 4.2 入力負荷の軽減

音声入力とローカルAI（Ollama）を利用し、Issue登録作業を支援できること。

AIは入力支援のみを行い、業務データの最終決定は利用者が行う。

---

## 4.3 Project単位での管理

Issue、Comment、AttachmentをProject単位で一元管理できること。

---

## 4.4 保守性

シンプルで保守しやすい構成を採用し、将来的な機能追加に対応できること。

---

## 4.5 プラットフォーム

初期版はWindows 11上で運用する。

将来的にはUbuntu Serverへ移行可能な設計とする。

---

# 5. Users

本システムの利用者を以下に定義する。

| 利用者           | 説明                                         | 主な利用機能                                                                               |
| ------------- | ------------------------------------------ | ------------------------------------------------------------------------------------ |
| Administrator | システム管理者。Project管理、ユーザー管理および各種マスタデータの管理を行う。 | Administration                                                                       |
| Engineer      | コミッショニング担当者。Issueの登録・更新・確認を行う。             | Project Selection、Issue Management、AI Draft、Comment Management、Attachment Management |

---

## 5.1 Administrator

Administratorはシステム全体を管理する。

主な責務は以下のとおりとする。

* ユーザーを管理する。
* Projectを管理する。
* マスタデータを管理する。
* システムを運用する。

初期版では、Project管理、ユーザー管理およびマスタデータ管理はCLIまたはCSVを利用して実施する。

Administratorはシステム上のロールであり、必ずしも専任の担当者を意味しない。

プロジェクトの規模に応じて、EngineerがAdministratorを兼任することを許容する。

マスタデータには、Room、RoomTypeなどのシステム運用に必要な管理データを含む。

---

## 5.2 Engineer

Engineerは日常的に本システムを利用する利用者である。

主な責務は以下のとおりとする。

* Projectを選択する。
* Issueを登録する。
* Issueを更新する。
* IssueのStatusを変更する。
* Commentを追加する。
* Attachmentを追加する。
* AI Draftを利用する。

Engineerはマスタデータを変更できない。

---

## 5.3 Future Expansion

将来的には以下のロールを追加できる設計とする。

| 利用者      | 想定用途           |
| -------- | -------------- |
| Viewer   | Issue閲覧専用      |
| Manager  | Project全体の進捗管理 |
| Customer | オーナー・施主向け閲覧専用  |

追加ロールは既存設計へ大きな影響を与えないよう、拡張可能な認可設計を採用する。

---

# 6. System Overview

CIM（Commissioning Issue Manager）は、Lutronシステムのコミッショニング業務において発生するIssueを効率的に管理するためのWebアプリケーションである。

本システムはPCおよびスマートフォンから利用できることを前提とする。

利用者はProjectを選択し、Issueの登録・更新・確認を行う。

IssueにはCommentおよびAttachmentを追加できる。

また、音声入力とローカルAI（Ollama）を利用し、Issue登録を支援する。

AIは入力支援のみを担当し、業務データの最終決定は利用者が行う。

---

## 6.1 System Configuration

初期版のシステム構成を以下に示す。

| 項目           | 内容                         |
| ------------ | -------------------------- |
| Client       | Web Browser（PC・Smartphone） |
| Backend      | FastAPI                    |
| Database     | SQLite                     |
| AI           | Ollama                     |
| File Storage | Local Storage              |

---

## 6.2 Target Environment

| 項目                      | 内容                           |
| ----------------------- | ---------------------------- |
| Development Environment | Windows 11 + WSL2 Ubuntu LTS |
| Initial Deployment      | Windows 11                   |
| Future Deployment       | Ubuntu Server                |

システムはOS依存を避け、将来的にUbuntu Serverへ移行可能な設計とする。

---

## 6.3 System Characteristics

本システムは以下の特徴を持つ。

* Project単位でIssueを管理する。
* ローカル環境で動作する。
* AIは入力支援のみを行う。
* シンプルで保守しやすい構成を採用する。
* 将来的な機能拡張を考慮した設計とする。

---

# 7. Functional Requirements

本章では、本システムが満たすべき機能要件を定義する。

---

## 7.1 Authentication

### 概要

利用者認証を行う。

### Requirements

| ID     | Requirement                 |
| ------ | --------------------------- |
| FR-001 | 利用者はログインできなければならない。         |
| FR-002 | 認証済み利用者のみシステムを利用できなければならない。 |
| FR-003 | 利用者はログアウトできなければならない。        |

---

## 7.2 Project Selection

### 概要

Engineerが作業対象となるProjectを選択する。

### Requirements

| ID     | Requirement                        |
| ------ | ---------------------------------- |
| FR-004 | Engineerは担当Projectを選択できなければならない。   |
| FR-005 | Engineerは選択中のProjectを変更できなければならない。 |
| FR-006 | Issueは選択したProjectに属さなければならない。      |

---

## 7.3 Issue Management

### 概要

Issueの登録・更新・参照を行う。

### Requirements

| ID     | Requirement                         |
| ------ | ----------------------------------- |
| FR-007 | EngineerはIssue一覧を表示できなければならない。      |
| FR-008 | EngineerはIssue詳細を表示できなければならない。      |
| FR-009 | EngineerはIssueを登録できなければならない。        |
| FR-010 | EngineerはIssueを更新できなければならない。        |
| FR-011 | EngineerはIssueのStatusを変更できなければならない。 |
| FR-012 | 初期版ではIssue削除機能を提供しない。               |

---

## 7.4 AI Draft

### 概要

AIによるIssue登録支援を行う。

### Requirements

| ID     | Requirement                                    |
| ------ | ---------------------------------------------- |
| FR-013 | Engineerは音声入力からAI Draftを生成できなければならない。          |
| FR-014 | AIはTargetTypeを推定しなければならない。                     |
| FR-015 | AIはTargetを推定しなければならない。                         |
| FR-016 | AIはCategoryを推定しなければならない。                       |
| FR-017 | AIはDescriptionを生成しなければならない。                    |
| FR-018 | AIはIssueを保存してはならない。                            |
| FR-019 | EngineerはAI Draftを確認・修正した後にIssueを登録できなければならない。 |

---

## 7.5 Comment Management

### 概要

IssueへCommentを追加する。

### Requirements

| ID     | Requirement                    |
| ------ | ------------------------------ |
| FR-020 | EngineerはCommentを追加できなければならない。 |
| FR-021 | Commentは履歴として保持しなければならない。      |
| FR-022 | 初期版ではComment編集機能を提供しない。        |
| FR-023 | 初期版ではComment削除機能を提供しない。        |

---

## 7.6 Attachment Management

### 概要

Issueへ写真・動画を添付する。

### Requirements

| ID     | Requirement                       |
| ------ | --------------------------------- |
| FR-024 | EngineerはAttachmentを追加できなければならない。 |
| FR-025 | EngineerはAttachmentを削除できなければならない。 |
| FR-026 | 初期版ではAttachment編集機能を提供しない。        |

---

## 7.7 Administration

### 概要

Administratorがシステム管理機能を利用する。

Administrationは以下の機能で構成する。

* Project Management
* User Management
* Master Data Management

---

### 7.7.1 Project Management

| ID     | Requirement                         |
| ------ | ----------------------------------- |
| FR-027 | AdministratorはProjectを登録できなければならない。 |
| FR-028 | AdministratorはProjectを更新できなければならない。 |
| FR-029 | AdministratorはProjectを管理できなければならない。 |
| FR-030 | 初期版ではCLIまたはCSVによる管理を行わなければならない。     |

---

### 7.7.2 User Management

| ID     | Requirement                     |
| ------ | ------------------------------- |
| FR-031 | Administratorは利用者を管理できなければならない。 |
| FR-032 | 初期版ではCLIまたはCSVによる管理を行わなければならない。 |

---

### 7.7.3 Master Data Management

対象となるマスタデータは以下を含む。

* Room
* RoomType

### Requirements

| ID     | Requirement                        |
| ------ | ---------------------------------- |
| FR-033 | Administratorはマスタデータを管理できなければならない。 |
| FR-034 | 初期版ではCLIまたはCSVによる管理を行わなければならない。    |
| FR-035 | 将来的に管理対象マスタを追加できる設計としなければならない。     |

---

# 8. Non-functional Requirements

本章では、本システムが満たすべき非機能要件を定義する。

---

## 8.1 Performance

### Requirements

| ID      | Requirement                               |
| ------- | ----------------------------------------- |
| NFR-001 | 一般的な業務利用において快適に操作できる応答性能を提供しなければならない。     |
| NFR-002 | 同一プロジェクト内のIssue一覧を適切な時間内に表示できなければならない。    |
| NFR-003 | AI Draft生成中であっても、システム全体の操作性を著しく損なってはならない。 |

---

## 8.2 Availability

### Requirements

| ID      | Requirement                   |
| ------- | ----------------------------- |
| NFR-004 | システムはローカル環境で安定して動作しなければならない。  |
| NFR-005 | システム障害発生時には、安全に再起動できなければならない。 |

---

## 8.3 Maintainability

### Requirements

| ID      | Requirement                 |
| ------- | --------------------------- |
| NFR-006 | システムは保守しやすい構成でなければならない。     |
| NFR-007 | レイヤードアーキテクチャを採用しなければならない。   |
| NFR-008 | 業務ロジックとデータアクセスを分離しなければならない。 |
| NFR-009 | 将来的な機能追加に対応できる構成でなければならない。  |

---

## 8.4 Security

### Requirements

| ID      | Requirement                    |
| ------- | ------------------------------ |
| NFR-010 | 認証されていない利用者はシステムを利用できてはならない。   |
| NFR-011 | 利用者は自身の権限に応じた機能のみ利用できなければならない。 |
| NFR-012 | AIは利用者の承認なしに業務データを変更してはならない。   |

---

## 8.5 Usability

### Requirements

| ID      | Requirement                         |
| ------- | ----------------------------------- |
| NFR-013 | PCおよびスマートフォンから利用できなければならない。         |
| NFR-014 | コミッショニング現場で直感的に操作できるUIを提供しなければならない。 |
| NFR-015 | 音声入力を利用してIssue登録作業を支援できなければならない。    |

---

## 8.6 Portability

### Requirements

| ID      | Requirement                         |
| ------- | ----------------------------------- |
| NFR-016 | 初期版はWindows 11で動作しなければならない。         |
| NFR-017 | 将来的にUbuntu Serverへ移行できる設計でなければならない。 |
| NFR-018 | OS依存の実装を最小限に抑えなければならない。             |

---

# 9. Data Requirements

本章では、本システムが管理するデータに関する要件を定義する。

---

## 9.1 Master Data

本システムでは以下のマスタデータを管理する。

* User
* Project
* RoomType
* Room

### Requirements

| ID     | Requirement            |
| ------ | ---------------------- |
| DR-001 | Userを管理できなければならない。     |
| DR-002 | Projectを管理できなければならない。  |
| DR-003 | RoomTypeを管理できなければならない。 |
| DR-004 | Roomを管理できなければならない。     |

---

## 9.2 Business Data

本システムでは以下の業務データを管理する。

* Issue
* Comment
* Attachment

### Requirements

| ID     | Requirement              |
| ------ | ------------------------ |
| DR-005 | Issueを管理できなければならない。      |
| DR-006 | Commentを管理できなければならない。    |
| DR-007 | Attachmentを管理できなければならない。 |

---

## 9.3 Data Relationships

データは以下の関係を持つ。

* Projectは複数のIssueを持つ。
* Issueは複数のCommentを持つ。
* Issueは複数のAttachmentを持つ。
* RoomはRoomTypeに属する。

### Requirements

| ID     | Requirement                       |
| ------ | --------------------------------- |
| DR-008 | Issueは必ず1つのProjectに属さなければならない。    |
| DR-009 | Commentは必ず1つのIssueに属さなければならない。    |
| DR-010 | Attachmentは必ず1つのIssueに属さなければならない。 |
| DR-011 | Roomは必ず1つのRoomTypeに属さなければならない。    |

---

## 9.4 Data Storage

### Requirements

| ID     | Requirement                       |
| ------ | --------------------------------- |
| DR-012 | 業務データはSQLiteへ保存しなければならない。         |
| DR-013 | 添付ファイルはLocal Storageへ保存しなければならない。 |
| DR-014 | 添付ファイルの管理情報はSQLiteで管理しなければならない。   |
| DR-015 | データの整合性を維持しなければならない。              |

---

# 10. AI Requirements

本章では、本システムにおけるAI利用に関する要件を定義する。

---

## 10.1 AI Usage Policy

本システムではローカルLLM（Ollama）を利用する。

AIは利用者の入力を支援するために利用し、業務上の最終判断は常に利用者が行う。

---

## 10.2 AI Requirements

| ID      | Requirement                  |
| ------- | ---------------------------- |
| AIR-001 | AIは音声入力を解析できなければならない。        |
| AIR-002 | AIはTargetTypeを推定できなければならない。  |
| AIR-003 | AIはTargetを推定できなければならない。      |
| AIR-004 | AIはCategoryを推定できなければならない。    |
| AIR-005 | AIはDescriptionを生成できなければならない。 |
| AIR-006 | AIはIssueを保存してはならない。          |
| AIR-007 | AIは利用者の承認なしに業務データを変更してはならない。 |
| AIR-008 | AIによる生成結果は利用者が編集できなければならない。  |

---

# 11. Operational Requirements

本章では、システム運用に関する要件を定義する。

---

## 11.1 Initial Operation

初期版はWindows 11環境で運用する。

---

## 11.2 System Management

Administratorは以下を管理できなければならない。

* Project
* User
* Master Data

初期版ではCLIまたはCSVを利用して管理を行う。

---

## 11.3 Backup

| ID     | Requirement               |
| ------ | ------------------------- |
| OR-001 | システムデータをバックアップできなければならない。 |
| OR-002 | バックアップデータから復元できなければならない。  |

---

# 12. Constraints

本章では、初期版におけるシステム制約を定義する。

| ID    | Constraint                                      |
| ----- | ----------------------------------------------- |
| C-001 | 初期版ではSQLiteを利用する。                               |
| C-002 | 初期版ではローカルストレージへ添付ファイルを保存する。                     |
| C-003 | 初期版ではProject、UserおよびMaster DataはCLIまたはCSVで管理する。 |
| C-004 | 初期版ではIssue削除機能を提供しない。                           |
| C-005 | 初期版ではComment編集・削除機能を提供しない。                      |
| C-006 | 初期版ではAttachment編集機能を提供しない。                      |

---

# 13. Future Enhancements

将来的に以下の機能追加を検討する。

* Viewerロール
* Managerロール
* Customerロール
* Web画面によるProject管理
* Web画面によるUser管理
* Web画面によるMaster Data管理
* Ubuntu Serverへのデプロイ
* Docker対応
* クラウド環境への展開
* AI機能の高度化

これらは初期版の要件には含めない。

---

# 14. Glossary

| 用語            | 説明                                 |
| ------------- | ---------------------------------- |
| AI Draft      | AIが生成したIssue登録候補                   |
| Attachment    | Issueへ添付する写真・動画などのファイル             |
| Category      | Issueの分類                           |
| Comment       | Issueに対するコメント                      |
| Commissioning | システムの現地試験・調整・引き渡し作業                |
| Engineer      | コミッショニング担当者                        |
| Hotel         | Projectの対象となる施設                    |
| Issue         | コミッショニング中に発見された課題・不具合・確認事項         |
| Local Storage | 添付ファイルを保存するローカルディレクトリ              |
| Master Data   | Project、User、RoomType、Roomなどの基礎データ |
| Ollama        | ローカルで動作するLLM実行環境                   |
| Project       | コミッショニング対象となる案件                    |
| Room          | 建物内の部屋                             |
| RoomType      | Roomの分類                            |
| Status        | Issueの進捗状態                         |
| Target        | Issueの対象機器・対象箇所                    |
| TargetType    | Targetの分類                          |
| User          | システム利用者                            |

---

# End of Document
