# CIM Requirements Specification

**Document Version:** 1.1 **Status:** Review **Last Updated:** 2026-07-03 **Author:** Masato Nagata

---

# Revision History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Reflect design review results and update master data and authentication requirements.|

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

本書は、 CIM (Commissioning Issue Manager) の要件を定義することを目的とする。

本書では、本システムが満たすべき機能要件、非機能要件、データ要件、 AI 要件、および運用要件を定義する。

本書を基に、基本設計、詳細設計、実装およびテストを実施する。

---

# 2. Scope

本書では以下を対象とする。

- システムの目的
- 利用者
- システム概要
- 機能要件
- 非機能要件
- データ要件
- AI要件
- 運用要件
- システム制約
- 将来拡張

以下は本書の対象外とする。

- データベース設計
- API 設計
- UI 設計
- クラス設計
- テスト設計

これらは各設計書で定義する。

---

# 3. Background

Lutron システムのコミッショニングでは、多数の Issue が発生する。

現場では Microsoft Teams や Excel などを利用して Issue を管理することが多く、以下の課題が存在する。

- Issue 管理が属人的になりやすい。
- 音声メモから Issue を整理する作業に時間を要する。
- 写真・動画と Issue の関連付けが煩雑である。
- Room 、RoomType 、Location 単位で Issue を整理しづらい。
- Project 全体の進捗や未解決 Issue を把握しづらい。

これらの課題を解決するため、コミッショニング業務に特化した Issue 管理システムとして CIM を開発する。

---

# 4. Goals

本システムの目的を以下に示す。

## 4.1 Issue 管理の効率化

コミッショニング時に発生する Issue を迅速かつ正確に登録・管理できること。

---

## 4.2 入力負荷の軽減

音声入力とローカルAI（Ollama）を利用し、 Issue 登録作業を支援できること。

AI は入力支援のみを行い、業務データの最終決定は利用者が行う。

---

## 4.3 Project単位での管理

Issue、 Comment、 Attachment を Project 単位で一元管理できること。

---

## 4.4 保守性

シンプルで保守しやすい構成を採用し、将来的な機能追加に対応できること。

---

## 4.5 プラットフォーム

初期版は Windows 11 上で運用する。

将来的には Ubuntu Server へ移行可能な設計とする。

---

# 5. Users

本システムの利用者を以下に定義する。

---

|利用者|説明|主な利用機能|
|---|---|---|
|Administrator|システム管理者。 Project 管理、ユーザー管理および各種マスタデータの管理を行う。|Administration|
|Engineer|コミッショニング担当者。 Issue の登録・更新・確認を行う。|Project Selection、 Issue Management、 AI Draft、 Comment Management、 Attachment Management|

---

## 5.1 Administrator

Administrator はシステム全体を管理する。

主な責務は以下のとおりとする。

- ユーザーを管理する。
- Hotel を管理する。
- Project を管理する。
- RoomType を管理する。
- Room を管理する。
- システムを運用する。

初期版では、 Hotel、 Project、 RoomType、 Room およびユーザーの管理は CLI または CSV を利用して実施する。

Administrator はシステム上のロールであり、必ずしも専任の担当者を意味しない。

プロジェクトの規模に応じて、 Engineer が Administrator を兼任することを許容する。

---

## 5.2 Engineer

Engineer は日常的に本システムを利用する利用者である。

主な責務は以下のとおりとする。

- Project を選択する。
- Issue を登録する。
- Issue を更新する。
- Issue の Status を変更する。
- Comment を追加する。
- Attachment を追加する。
- AI Draft を利用する。

Engineer はマスタデータを変更できない。

---

## 5.3 Future Expansion

将来的には以下のロールを追加できる設計とする。

|利用者|想定用途|
|---|---|
|Viewer|Issue 閲覧専用|
|Manager|Project 全体の進捗管理|
|Customer|オーナー・施主向け閲覧専用|

追加ロールは既存設計へ大きな影響を与えないよう、拡張可能な認可設計を採用する。

---

# 6. System Overview

CIM（Commissioning Issue Manager）は、 Lutron システムのコミッショニング業務において発生する Issue を効率的に管理するための Web アプリケーションである。

本システムはPCおよびスマートフォンから利用できることを前提とする。

利用者は Project を選択し、 Issue の登録・更新・確認を行う。

Issue には Comment および Attachment を追加できる。

また、音声入力とローカルAI（Ollama）を利用し、 Issue 登録を支援する。

AI は入力支援のみを担当し、業務データの最終決定は利用者が行う。

---

## 6.1 System Configuration

初期版のシステム構成を以下に示す。

|項目|内容|
|---|---|
|Client|Web Browser（PC・Smartphone）|
|Backend|FastAPI|
|Database|SQLite|
|AI|Ollama|
|File Storage|Local Storage|

---

## 6.2 Target Environment

|項目|内容|
|---|---|
|Development Environment|Windows 11 + WSL2 Ubuntu LTS|
|Initial Deployment|Windows 11|
|Future Deployment|Ubuntu Server|

システムは OS 依存を避け、将来的に Ubuntu Server へ移行可能な設計とする。

---

## 6.3 System Characteristics

本システムは以下の特徴を持つ。

- Project 単位 で Issue を管理する。
- ローカル環境で動作する。
- AI は入力支援のみを行う。
- シンプルで保守しやすい構成を採用する。
- 将来的な機能拡張を考慮した設計とする。

---

# 7. Functional Requirements

本章では、本システムが満たすべき機能要件を定義する。

---

## 7.1 Authentication

### 概要

利用者認証を行う。

### Requirements

|ID|Requirement|
|---|---|
|FR-001|利用者はログインできなければならない。|
|FR-002|認証済み利用者のみシステムを利用できなければならない。|
|FR-003|利用者はログアウトできなければならない。|

---

## 7.2 Project Selection

### 概要

Engineer が作業対象となる Project を選択する。

### Requirements

|ID|Requirement|
|---|---|
|FR-004|Engineer は担当 Project を選択できなければならない。|
|FR-005|Engineer は選択中の Project を変更できなければならない。|
|FR-006|Issue は選択した Project に属さなければならない。|

---

## 7.3 Issue Management

### 概要

Issue の登録・更新・参照を行う。

### Requirements

|ID|Requirement|
|---|---|
|FR-007|Engineer は Issue 一覧を表示できなければならない。|
|FR-008|Engineer は Issue 詳細を表示できなければならない。|
|FR-009|Engineer は Issue を登録できなければならない。|
|FR-010|Engineer は Issue を更新できなければならない。|
|FR-011|Engineer は Issue の Status を変更できなければならない。|
|FR-012|初期版では Issue 削除機能を提供しない。|

---

## 7.4 AI Draft

### 概要

AI による Issue 登録支援を行う。

### Requirements

|ID|Requirement|
|---|---|
|FR-013|Engineer は音声入力から AI Draft を生成できなければならない。|
|FR-014|AI は TargetType を推定しなければならない。|
|FR-015|AI は Target を推定しなければならない。|
|FR-016|AI は Category を推定しなければならない。|
|FR-017|AI は Description を生成しなければならない。|
|FR-018|AI は Issue を保存してはならない。|
|FR-019|Engineer は AI Draft を確認・修正した後に Issue を登録できなければならない。|

---

## 7.5 Comment Management

### 概要

Issue へ Comment を追加する。

### Requirements

|ID|Requirement|
|---|---|
|FR-020|Engineer は Comment を追加できなければならない。|
|FR-021|Comment は履歴として保持しなければならない。|
|FR-022|初期版では Comment 編集機能を提供しない。|
|FR-023|初期版では Comment 削除機能を提供しない。|

---

## 7.6 Attachment Management

### 概要

Issue へ写真・動画を添付する。

### Requirements

|ID|Requirement|
|---|---|
|FR-024|Engineer は Attachment を追加できなければならない。|
|FR-025|Engineer は Attachment を削除できなければならない。|
|FR-026|初期版では Attachment 編集機能を提供しない。|

---

## 7.7 Administration

### 概要

Administrator がシステム管理機能を利用する。

Administration は以下の機能で構成する。

- Project Management
- User Management
- Master Data Management

---

### 7.7.1 Project Management

|ID|Requirement|
|---|---|
|FR-027|Administrator は Project を登録できなければならない。|
|FR-028|Administrator は Project を更新できなければならない。|
|FR-029|Administrator は Project を管理できなければならない。|
|FR-030|初期版では CLI または CSV による管理を行わなければならない。|

---

### 7.7.2 User Management

|ID|Requirement|
|---|---|
|FR-031|Administrator は利用者を管理できなければならない。|
|FR-032|初期版では CLI または CSV による管理を行わなければならない。|

---

### 7.7.3 Master Data Management

対象となるマスタデータは以下を含む。

- Hotel
- RoomType
- Room
- Location

### Requirements

|ID|Requirement|
|---|---|
|FR-033|Administrator はマスタデータを管理できなければならない。|
|FR-034|初期版では CLI または CSV による管理を行わなければならない。|
|FR-035|将来的に管理対象マスタを追加できる設計としなければならない。|

---

# 8. Non-functional Requirements

本章では、本システムが満たすべき非機能要件を定義する。

---

## 8.1 Performance

### Requirements

|ID|Requirement|
|---|---|
|NFR-001|一般的な業務利用において快適に操作できる応答性能を提供しなければならない。|
|NFR-002|同一プロジェクト内の Issue 一覧を適切な時間内に表示できなければならない。|
|NFR-003|AI Draft 生成中であっても、システム全体の操作性を著しく損なってはならない。|

---

## 8.2 Availability

### Requirements

|ID|Requirement|
|---|---|
|NFR-004|システムはローカル環境で安定して動作しなければならない。|
|NFR-005|システム障害発生時には、安全に再起動できなければならない。|

---

## 8.3 Maintainability

### Requirements

|ID|Requirement|
|---|---|
|NFR-006|システムは保守しやすい構成でなければならない。|
|NFR-007|レイヤードアーキテクチャを採用しなければならない。|
|NFR-008|業務ロジックとデータアクセスを分離しなければならない。|
|NFR-009|将来的な機能追加に対応できる構成でなければならない。|

---

## 8.4 Security

### Requirements

|ID|Requirement|
|---|---|
|NFR-010|認証されていない利用者はシステムを利用できてはならない。|
|NFR-011|利用者は自身の権限に応じた機能のみ利用できなければならない。|
|NFR-012|AI は利用者の承認なしに業務データを変更してはならない。|

---

## 8.5 Usability

### Requirements

|ID|Requirement|
|---|---|
|NFR-013|PC およびスマートフォンから利用できなければならない。|
|NFR-014|コミッショニング現場で直感的に操作できるUIを提供しなければならない。|
|NFR-015|音声入力を利用して Issue 登録作業を支援できなければならない。|

---

## 8.6 Portability

### Requirements

|ID|Requirement|
|---|---|
|NFR-016|初期版は Windows 11 で動作しなければならない。|
|NFR-017|将来的に Ubuntu Server へ移行できる設計でなければならない。|
|NFR-018|OS 依存の実装を最小限に抑えなければならない。|

---

# 9. Data Requirements

本章では、本システムが管理するデータに関する要件を定義する。

---

## 9.1 Master Data

本システムでは以下のマスタデータを管理する。

- User
- Hotel
- Project
- RoomType
- Room

### Requirements

|ID|Requirement|
|---|---|
|DR-001|User を管理できなければならない。|
|DR-002|Hotel を管理できなければならない。|
|DR-003|Project を管理できなければならない。|
|DR-004|RoomType を管理できなければならない。|
|DR-005|Room を管理できなければならない。|

User は、 username 、 password_hash 、 display_name および role を管理する。

username はログインIDとして利用する。

username には任意の文字列を利用できる。メールアドレス形式も許容する。

初期版では、 email は独立した管理項目として扱わない。

Hotel 、 Project および RoomType は name を管理する。

初期版では、 Hotel Code 、 Project Code および RoomType Code は管理しない。

---

## 9.2 Business Data

本システムでは以下の業務データを管理する。

- Issue
- Comment
- Attachment

### Requirements

|ID|Requirement|
|---|---|
|DR-006|Issue を管理できなければならない。|
|DR-007|Comment を管理できなければならない。|
|DR-008|Attachment を管理できなければならない。|

---

## 9.3 Data Relationships

データは以下の関係を持つ。

- Hotel は複数の RoomType を持つ。
- Hotel は複数の Room を持つ。
- Hotel は複数の Project を持つ。
- Room は RoomType に属する。
- Project は複数の Issue を持つ。
- Issue は必要に応じて Room を参照する。
- Issue は複数の Comment を持つ。
- Issue は複数の Attachment を持つ。

### Requirements

|ID|Requirement|
|---|---|
|DR-009|RoomType は必ず 1 つの Hotel に属さなければならない。|
|DR-010|Room は必ず 1 つの Hotel に属さなければならない。|
|DR-011|Project は必ず 1 つの Hotel に属さなければならない。|
|DR-012|Room は必ず 1 つの RoomType に属さなければならない。|
|DR-013|Issue は必ず 1 つの Project に属さなければならない。|
|DR-014|Issue は必要に応じて Room を参照できる。|
|DR-015|Comment は必ず 1 つの Issue に属さなければならない。|
|DR-016|Attachment は必ず 1 つの Issue に属さなければならない。|

---

## 9.4 Data Storage

### Requirements

|ID|Requirement|
|---|---|
|DR-017|業務データは SQLite へ保存しなければならない。|
|DR-018|添付ファイルは Local Storage へ保存しなければならない。|
|DR-019|添付ファイルの管理情報は SQLite で管理しなければならない。|
|DR-020|データの整合性を維持しなければならない。|

---

# 10. AI Requirements

本章では、本システムにおけるAI利用に関する要件を定義する。

---

## 10.1 AI Usage Policy

本システムではローカル LLM (Ollama) を利用する。

AIは利用者の入力を支援するために利用し、業務上の最終判断は常に利用者が行う。

---

## 10.2 AI Requirements

|ID|Requirement|
|---|---|
|AIR-001|AI は音声入力を解析できなければならない。|
|AIR-002|AI は TargetType を推定できなければならない。|
|AIR-003|AI は Target を推定できなければならない。|
|AIR-004|AI は Category を推定できなければならない。|
|AIR-005|AI は Description を生成できなければならない。|
|AIR-006|AI は Issue を保存してはならない。|
|AIR-007|AI は利用者の承認なしに業務データを変更してはならない。|
|AIR-008|AI による生成結果は利用者が編集できなければならない。|

---

# 11. Operational Requirements

本章では、システム運用に関する要件を定義する。

---

## 11.1 Initial Operation

初期版は Windows 11 環境で運用する。

---

## 11.2 System Management

Administratorは以下を管理できなければならない。

- Project
- User
- Master Data

初期版ではCLIまたはCSVを利用して管理を行う。

---

## 11.3 Backup

|ID|Requirement|
|---|---|
|OR-001|システムデータをバックアップできなければならない。|
|OR-002|バックアップデータから復元できなければならない。|

---

# 12. Constraints

本章では、初期版におけるシステム制約を定義する。

|ID|Constraint|
|---|---|
|C-001|初期版では SQLite を利用する。|
|C-002|初期版ではローカルストレージへ添付ファイルを保存する。|
|C-003|初期版では Project 、 User および Master Data は CLI または CSV で管理する。|
|C-004|初期版では Issue 削除機能を提供しない。|
|C-005|初期版では Comment 編集・削除機能を提供しない。|
|C-006|初期版では Attachment 編集機能を提供しない。|

---

# 13. Future Enhancements

将来的に以下の機能追加を検討する。

- Viewer ロール
- Manager ロール
- Customer ロール
- Web 画面による Project 管理
- Web 画面による User 管理
- Web 画面による Master Data 管理
- Ubuntu Server へのデプロイ
- Docker 対応
- クラウド環境への展開
- AI機能の高度化

これらは初期版の要件には含めない。

---

# 14. Glossary

|用語|説明|
|---|---|
|AI Draft|AI が生成した Issue 登録候補|
|Attachment|Issue へ添付する写真・動画などのファイル|
|Category|Issue の分類|
|Comment|Issue に対するコメント|
|Commissioning|システムの現地試験・調整・引き渡し作業|
|Engineer|コミッショニング担当者|
|Hotel|Project の対象となる施設|
|Issue|コミッショニング中に発見された課題・不具合・確認事項|
|Local Storage|添付ファイルを保存するローカルディレクトリ|
|Master Data|Hotel 、 Project 、 User 、 RoomType 、 Room などの基礎データ|
|Ollama|ローカルで動作する LLM 実行環境|
|Project|コミッショニング対象となる案件|
|Room|建物内の部屋|
|RoomType|Room の分類|
|Status|Issue の進捗状態|
|Target|Issue の対象機器・対象箇所|
|TargetType|Target の分類|
|User|システム利用者|

---

# End of Document
