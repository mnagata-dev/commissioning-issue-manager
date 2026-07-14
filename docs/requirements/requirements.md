# CIM Requirements Specification

- **Document Version:** 1.2
- **Status:** Draft
- **Last Updated:** 2026-07-08
- **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Reflect updated login specification and master data terminology.|
|1.2|2026-07-08|Refine the system architecture, clarify the domain model, redefine AI responsibilities, and improve the document as the primary design specification for the project.|

---

# Table of Contents

1. Purpose
2. Scope
3. Document Principles
4. Background
5. Users and Roles
6. System Overview
7. Functional Requirements
8. Non-functional Requirements
9. Data Requirements
10. AI Requirements
11. Constraints
12. Future Enhancements
13. Glossary

---

# 1. Purpose

本書は、Commissioning Issue Manager (CIM) の要件を定義することを目的とする。

本書は、本システムの目的、業務背景、利用シナリオ、設計方針、および機能要件を定義する最上位ドキュメントである。

本書を基準として、

- 基本設計
- データベース設計
- API 設計
- UI 設計
- 詳細設計
- テスト設計

を作成する。

---

# 2. Scope

本書では以下を定義する。

- システムの目的
- 業務背景
- 利用者
- 利用シナリオ
- システム概要
- 機能要件
- 非機能要件
- データ要件
- AI 要件
- 制約事項
- 将来拡張
- 用語

本書では以下は対象外とする。

- DB テーブル定義
- API 詳細仕様
- UI レイアウト
- クラス設計
- 実装方法
- テストケース

これらは各設計書で定義する。

---

# 3. Document Principles

## 3.1 Purpose of this Document

本書は、CIM の要件を定義する最上位ドキュメントである。

下位設計書は本書を基準として作成する。

本書と下位設計書の内容に矛盾がある場合は、本書を優先する。

---

## 3.2 Design Philosophy

本書は、単なる機能一覧ではなく、システム全体の目的および設計思想を定義する。

利用者がどのような業務を行い、その業務をどのように支援するかを明確にする。

各機能は、実際のコミッショニング業務を基準として定義する。

---

## 3.3 Intended Readers

本書は以下の利用者を対象とする。

- Product Owner
- Developer
- Tester
- Reviewer
- AI Assistant

本書のみを読んだ場合でも、本システムがどのような目的で利用されるかを理解できることを目標とする。

---

## 3.4 Update Policy

本書を更新する際は、個々の機能ではなく、システム全体の利用目的および業務フローとの整合性を優先する。

新しい要求を追加する場合は、既存の設計思想との整合性を確認する。

本書の更新後は、下位設計書との整合性を確認する。

---

# 4. Background

## 4.1 Project Background

Commissioning Issue Manager (CIM) は、Lutron 照明制御システムのコミッショニング業務を支援するための Web アプリケーションである。

コミッショニングでは、ホテル内の設備を実際に操作しながら動作確認を行い、不具合や調整事項を記録する。

現場では短時間で多数の Issue が発生するため、迅速かつ正確に記録できる仕組みが必要となる。

---

## 4.2 Purpose of the System

本システムは、コミッショニング現場で発見した Issue を記録・管理し、対応状況を共有することを目的とする。

一般的な Issue 管理システムではなく、コミッショニング業務に特化したシステムとして設計する。

---

## 4.3 Target Facilities

本システムでは、以下のような対象を管理する。

- Guest Room
- Lobby
- Restaurant
- Ballroom
- Corridor
- Network
- Control Panel

初期版では、Room 以外の対象は OTHER として管理する。

---

## 4.4 Basic Design Concept

本システムは、現場での入力負荷を最小限にすることを重視する。

利用者が現場で短時間に Issue を登録できるよう、必要最小限の入力で運用できる設計とする。

AI は入力作業を支援するが、最終的な判断および登録は必ず利用者が行う。

(User in Control)

---

# 5. Users and Roles

## 5.1 Overview

本システムでは、以下の利用者を定義する。

- Administrator
- Engineer

---

## 5.2 Administrator

Administrator は、本システム全体を管理する利用者である。

Administrator は Engineer が利用できるすべての機能を利用できる。

加えて、以下の管理業務を行う。

- Hotel 管理
- Project 管理
- User 管理
- Master Data 管理

初期版では、これらの管理は CLI または CSV により実施する。

将来的には Web UI による管理機能を提供する。

---

## 5.3 Engineer

Engineer は、コミッショニング現場で Issue を登録・管理する利用者である。

Engineer は以下の機能を利用できる。

- Project 選択
- Issue 登録
- Issue 更新
- Status 更新
- Comment 登録
- Attachment 登録
- AI Draft 利用

Engineer は管理者ではなく、Hotel や Master Data の管理は行わない。

---

## 5.4 User Responsibilities

Administrator と Engineer の責務を以下に示す。

|項目|Administrator|Engineer|
|---|:---:|:---:|
|Project Selection|✓|✓|
|Issue Management|✓|✓|
|Comment|✓|✓|
|Attachment|✓|✓|
|AI Draft|✓|✓|
|Hotel Management|✓|-|
|Project Management|✓|-|
|User Management|✓|-|
|Master Data Management|✓|-|

---

# 6. System Overview

## 6.1 Overview

本システムは、コミッショニング現場で発見した Issue を記録・管理するための Web アプリケーションである。

利用者は現場で設備を試験しながら、不具合や調整事項を登録し、対応状況を継続的に管理する。

本システムは、Issue のライフサイクル全体を支援する。

---

## 6.2 Typical Workflow

代表的な利用フローを以下に示す。

1. Administrator が Hotel を登録する。
2. Administrator が Hotel に属する Master Data を登録する。
3. Administrator が Project を作成する。
4. Engineer が Project を選択する。
5. Engineer が Issue Create を開く。
6. Engineer が Target Type を選択する。
7. Engineer が対象を指定する。
8. Engineer が音声入力またはテキスト入力を行う。
9. AI が Issue Draft を生成する。
10. Engineer が内容を確認・修正する。
11. Engineer が Issue を登録する。
12. Engineer が必要に応じて Comment および Attachment を追加する。
13. Engineer が Status を更新しながら対応状況を管理する。

---

## 6.3 Target Selection

Issue は必ず対象を指定して登録する。

初期版では以下の 2 種類を提供する。

- ROOM
- OTHER

---

### ROOM

ROOM は客室を対象とする。

Engineer は Issue 登録前に Room を選択する。

AI は Room を推定しない。

---

### OTHER

OTHER は Room 以外の対象を表す。

例

- Lobby
- Ballroom
- Restaurant
- Corridor
- Network
- Processor
- Control Panel
- MDF
- IDF

Engineer は Target を自由入力する。

入力時は、過去の入力履歴から候補を選択できる。

初期版では履歴を localStorage に保存する。

---

## 6.4 AI Assisted Workflow

AI は入力支援機能として利用する。

利用者が音声入力またはテキスト入力を行い、その内容を基に AI Draft を生成する。

AI Draft は登録前の下書きであり、最終的な登録内容ではない。

利用者は AI Draft を確認し、必要に応じて修正した上で Issue を登録する。

---

## 6.5 User in Control

本システムでは User in Control を基本方針とする。

AI は利用者の作業を支援するものであり、最終的な判断を行わない。

利用者は AI が生成した内容を必ず確認し、必要に応じて修正してから登録する。

---

## 6.6 Input Assistance

Issue 登録時の入力負荷を軽減するため、入力補助機能を提供する。

初期版では以下を保存対象とする。

- Target Type
- Room
- Category

前回利用した値を初期値として表示する。

OTHER の Target は入力履歴を保持し、候補から選択できる。

---

## 6.7 Design Principles

本システムは以下の設計方針に基づいて設計する。

- User in Control
- Simplicity First
- Mobile First
- AI Assistance Only
- Master Data First

各設計書は、この設計方針を基準として作成する。

---

# 7. Functional Requirements

## 7.1 Overview

本システムは、コミッショニング現場における Issue のライフサイクル全体を支援する。

初期版では、Issue の登録、更新および進捗管理を中心機能とする。

---

## 7.2 Authentication

利用者は認証後に本システムを利用する。

認証では以下を使用する。

- Username
- Password

Username はログイン ID であり、メールアドレス形式も利用できる。

利用者は認証成功後に Project Selection を表示する。

---

## 7.3 Project Selection

利用者は作業対象となる Project を選択する。

選択した Project を基準として Issue を管理する。

Project は Hotel に属する案件を表す。

Project の例

- New Construction
- Renovation
- Maintenance

---

## 7.4 Issue Management

Issue は本システムの中心となる管理対象である。

利用者は以下を実施できる。

- Issue 登録
- Issue 更新
- Issue 一覧表示
- Issue 詳細表示
- Status 更新

Issue は Project に属する。

Issue は Room または OTHER を対象として登録する。

---

## 7.5 Target Type

初期版では以下の Target Type を提供する。

- ROOM
- OTHER

---

### ROOM

ROOM は客室を対象とする。

Room は利用者が UI で選択する。

AI は Room を推定しない。

---

### OTHER

OTHER は Room 以外の対象を表す。

Target は利用者が自由入力する。

入力時は過去の履歴を候補として表示する。

初期版では履歴を localStorage に保存する。

---

## 7.6 AI Draft

AI Draft は Issue 登録時の入力支援機能である。

利用者は音声入力またはテキスト入力を行い、AI Draft を生成する。

AI は入力内容を整理し、Issue Draft を作成する。

利用者は AI Draft を確認し、必要に応じて修正した後に登録する。

AI Draft は登録前の下書きであり、自動登録は行わない。

---

## 7.7 AI Generated Information

AI は以下の情報を生成する。

- Category
- Description

AI は以下を決定しない。

- Room
- Target Type
- Target

これらは利用者が指定する。

---

## 7.8 Comments

利用者は Issue に Comment を追加できる。

Comment は Issue の対応履歴を記録するために利用する。

Comment は時系列で管理する。

---

## 7.9 Attachments

利用者は Issue に画像および動画を添付できる。

初期版では複数ファイルの添付をサポートする。

Attachment は Issue に関連付けて管理する。

---

## 7.10 Status Management

Issue は以下の Status を持つ。

- Open
- In Progress
- Resolved
- Closed

Status は対応状況を表す。

利用者は対応状況に応じて Status を更新する。

---

## 7.11 Search

利用者は Issue を検索できる。

初期版では以下を検索条件として提供する。

- Keyword
- Status
- Category
- Target Type

検索結果は選択中の Project を対象とする。

---

## 7.12 Input Assistance

入力負荷を軽減するため、入力補助機能を提供する。

初期版では以下を前回入力値として保持する。

- Target Type
- Room
- Category

OTHER の Target は入力履歴を保持し、候補から選択できる。

---

## 7.13 Master Data Management

初期版では以下を Master Data とする。

- Hotel
- RoomType
- Room
- User

Master Data の登録および更新は Administrator が実施する。

初期版では CLI または CSV により管理する。

---

## 7.14 Administration

Administrator は以下を管理する。

- Hotel
- Project
- User
- Master Data

初期版では Web UI による管理機能は提供しない。

---

## 7.15 Auditability

Issue の対応履歴を追跡できるようにする。

以下の情報を保持する。

- Status
- Comment
- Attachment
- 更新日時
- 更新者

これにより、コミッショニング作業の進捗を継続的に管理できる。

---

# 8. Non-functional Requirements

## 8.1 Performance

通常利用において、画面操作に対して利用者が待ち時間を感じない応答性能を提供する。

AI Draft は AI の応答時間に依存するが、利用者に処理中であることを明確に表示する。

---

## 8.2 Availability

初期版はローカルネットワーク内で利用する。

クラウドサービスへの常時接続を前提としない。

---

## 8.3 Usability

コミッショニング現場での利用を想定し、短時間で Issue を登録できる UI とする。

入力項目は必要最小限とする。

---

## 8.4 Portability

初期版は Windows 上で動作する。

将来的に Linux 環境へ移行できる設計とする。

Windows 固有機能への依存は避ける。

---

## 8.5 Maintainability

各レイヤーの責務を明確に分離する。

実装は保守性を重視した構成とする。

---

## 8.6 Extensibility

初期版ではシンプルな構成を採用する。

将来的な機能追加に対応できる設計とする。

例

- Location
- Dashboard
- Web Administration
- Cloud Deployment
- PostgreSQL

---

# 9. Data Requirements

## 9.1 Overview

本システムでは、Hotel ごとに Project および Master Data を管理する。

Issue は Project に属し、コミッショニング中に発見した不具合または調整事項を表す。

データモデルは、現場での運用を重視し、必要最小限の構成を採用する。

---

## 9.2 Master Data

初期版では以下を Master Data とする。

- Hotel
- RoomType
- Room
- User

Administrator は Project 作成前に Master Data を登録する。

初期版では CLI または CSV を利用して登録する。

---

## 9.3 Data Relationships

本システムでは、以下の関係を採用する。

```text
Hotel
├── RoomType
├── Room
└── Project
     └── Issue
          ├── Room (optional)
          ├── Comment
          └── Attachment

User
```

Relationship は以下のとおりである。

|Parent|Cardinality|Child|
|---|---|---|
|Hotel|1 : N|RoomType|
|Hotel|1 : N|Room|
|Hotel|1 : N|Project|
|RoomType|1 : N|Room|
|Project|1 : N|Issue|
|Issue|1 : N|Comment|
|Issue|1 : N|Attachment|

Room は Hotel に属する。

Room は Project に属さない。

Project は Hotel に属する案件である。

Issue は Project に属し、対象を表す Room または OTHER を保持する。

---

## 9.4 Room

Room は Hotel 内の客室を表す。

Room は必ず RoomType を参照する。

Room は Master Data であり、Project ごとに作成しない。

---

## 9.5 RoomType

RoomType は Hotel に属する。

RoomType は同一 Hotel 内の Room の分類を表す。

例

- Standard Twin
- Deluxe Twin
- Suite

---

## 9.6 Project

Project は Hotel に対するコミッショニング案件を表す。

例

- New Construction
- Renovation
- Maintenance

Project は Room を所有しない。

---

## 9.7 Issue

Issue は Project に属する。

Issue はコミッショニング時に発見した不具合または調整事項を表す。

Issue は以下の対象を持つ。

- ROOM
- OTHER

---

### ROOM

Room を参照する。

---

### OTHER

Target を文字列として保持する。

例

- Lobby
- Ballroom
- Network
- MDF
- IDF
- Processor

---

## 9.8 Location

初期版では Location テーブルは作成しない。

Room 以外の対象は OTHER として管理する。

Location は将来的な拡張候補とする。

---

## 9.9 Target Type

初期版では以下を提供する。

- ROOM
- OTHER

将来的に必要となった場合のみ、新しい Target Type を追加する。

---

## 9.10 Data Retention

Issue、Comment および Attachment はコミッショニング履歴として保持する。

初期版では物理削除を行わない。

---

# 10. AI Requirements

## 10.1 Purpose

AI はコミッショニング作業を支援する入力補助機能として利用する。

AI は利用者の代わりに判断するものではない。

---

## 10.2 Responsibilities

AI は以下を担当する。

- 音声入力の解析
- テキスト入力の解析
- Category の提案
- Description の生成

---

## 10.3 Out of Scope

AI は以下を行わない。

- Room の決定
- Target Type の決定
- Target の決定
- Issue の自動登録
- Status の変更

これらは利用者が行う。

---

## 10.4 User in Control

AI が生成した内容は Draft として扱う。

利用者は必ず内容を確認し、必要に応じて修正してから登録する。

AI が生成した内容をそのまま登録することを前提としない。

---

## 10.5 AI Failure

AI Draft を生成できない場合でも、利用者は手動で Issue を登録できる。

AI は必須機能ではなく、入力支援機能である。

---

# 11. Constraints

## 11.1 Initial Release

初期版では以下を採用する。

- FastAPI
- SQLite
- Local File Storage
- Ollama
- Local AI
- Browser UI

---

## 11.2 Excluded Features

初期版では以下を対象外とする。

- Web による Master Data 管理
- Location 管理
- Dashboard
- Report 機能
- Cloud 運用
- PostgreSQL
- Docker 必須運用

これらは将来的な拡張とする。

---

## 11.3 Design Constraints

初期版ではシンプルな構成を優先する。

過度な汎用化は行わず、実際のコミッショニング業務に必要な機能を優先して実装する。

将来拡張を考慮しつつ、不要な複雑化を避ける。

---

# 12. Future Enhancements

## 12.1 Basic Policy

初期版では、コミッショニング現場で必要となる機能を優先して提供する。

将来的な拡張を考慮した設計とするが、初期版では実装しない機能は要求として定義しない。

---

## 12.2 Functional Enhancements

将来的に以下の機能追加を検討する。

- Web UI による Master Data Management
- Location Management
- Dashboard
- Report Generation
- Statistics
- Advanced Search
- Notification
- Offline Support
- Multi-language Support
- Dark Mode
- Tablet Optimized UI

---

## 12.3 AI Enhancements

将来的に以下の AI 機能を検討する。

- Category 推定精度の向上
- Description 自動補完
- 類似 Issue の提案
- ナレッジ検索
- Issue 要約
- Issue 分析

AI は将来も入力支援を目的とし、利用者に代わって最終判断を行わない。

---

## 12.4 Deployment Enhancements

将来的に以下の運用を検討する。

- Docker
- PostgreSQL
- Linux Server
- Cloud Deployment
- Remote Access

---

# 13. Glossary

|Term|Description|
|---|---|
|Administrator|システム管理者。Engineer が利用できるすべての機能に加え、Hotel、Project、User および Master Data を管理する。|
|AI Draft|AI が生成する登録前の Issue 下書き。利用者による確認および修正を前提とする。|
|Attachment|Issue に添付する画像または動画。|
|Category|Issue を分類するための分類情報。|
|Comment|Issue に対する対応履歴または補足情報。|
|Commissioning|設備を実際に試験し、設計どおり動作することを確認する作業。|
|Engineer|コミッショニング作業を実施する利用者。|
|Hotel|Project および Master Data を管理する単位。|
|Issue|コミッショニング時に発見した不具合または調整事項。|
|Master Data|Hotel、RoomType、Room および User を表す基礎データ。|
|OTHER|Room 以外の対象を表す Target Type。|
|Project|Hotel に対するコミッショニング案件。|
|Room|Hotel 内の客室。RoomType を参照する。|
|RoomType|Hotel 内で利用する客室種別。|
|Status|Issue の対応状況。Open、In Progress、Resolved および Closed を持つ。|
|Target|Issue の対象。ROOM の場合は Room、OTHER の場合は自由入力した対象を表す。|
|Target Type|Issue の対象種別。初期版では ROOM および OTHER を提供する。|
|User in Control|AI は入力支援のみを行い、最終的な判断および登録は利用者が行うという設計思想。|

---

# End of Document
