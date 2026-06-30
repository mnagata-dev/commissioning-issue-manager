# Architecture Decision Records (ADR)

**Document Version:** 1.0
**Status:** Active
**Last Updated:** 2026-06-30
**Author:** Masato Nagata

---

# 1. Purpose

このディレクトリでは、CIM（Commissioning Issue Manager）プロジェクトにおける重要な設計判断（Architecture Decision Record: ADR）を管理する。

ADRは「何を決めたか」だけではなく、「なぜその設計を採用したのか」を記録するためのドキュメントである。

要件定義書・設計書では設計内容を定義し、ADRではその背景となる意思決定を記録する。

---

# 2. ADRとは

ADR（Architecture Decision Record）は、プロジェクト全体へ影響する重要な設計判断を記録する文書である。

ADRは以下のような判断を対象とする。

* 設計原則
* ドメインモデル
* アーキテクチャ
* データ管理方針
* AI利用方針
* API設計方針
* セキュリティ方針

一時的な実装方法やコーディングスタイルはADRではなく、設計書またはソースコードで管理する。

---

# 3. ADR一覧

| ADR     |   Status   | Category  | Title                   | Decision Summary                                               |
| ------- | :--------: | --------- | ----------------------- | -------------------------------------------------------------- |
| ADR-001 | ✅ Accepted | Principle | User in Control         | AIは補助機能とし、最終判断はユーザーが行う。                                        |
| ADR-002 | ✅ Accepted | Domain    | TargetType Definition   | TargetTypeは ROOM / ROOM_TYPE / AREA / HOTEL / GENERAL の5種類とする。 |
| ADR-003 | ✅ Accepted | Domain    | Category Definition     | Categoryは「ユーザーが最初に認識した対象（一次対象）」を表す。                            |
| ADR-004 | ✅ Accepted | Domain    | Room Model Design       | RoomはRoomTypeを参照し、floor_numberを保持しない。                          |
| ADR-005 | ✅ Accepted | Domain    | Issue as Aggregate Root | IssueをAggregate Rootとし、Comment・AttachmentはIssue配下で管理する。        |

---

# 4. Category

| Category     | 説明               |
| ------------ | ---------------- |
| Principle    | システム全体の設計思想・基本原則 |
| Domain       | ドメインモデルおよび業務ルール  |
| Architecture | システム構造・レイヤー構成    |
| Storage      | データ保存・ファイル管理     |
| API          | API設計方針          |
| Security     | 認証・認可・セキュリティ     |
| AI           | AI利用方針・AIワークフロー  |

---

# 5. ADR作成ルール

新しいADRを作成するのは、プロジェクト全体へ影響する重要な設計判断を行った場合とする。

以下のような変更はADRの対象とする。

* 設計原則の変更
* ドメインモデルの変更
* アーキテクチャの変更
* データ管理方針の変更
* AI利用方針の変更
* 認証方式の変更

以下は通常、ADRの対象としない。

* メソッド名の変更
* 実装方法の改善
* 軽微なリファクタリング
* UIレイアウトの調整
* コメントやドキュメントの修正

---

# 6. ADRテンプレート

すべてのADRは以下の構成で作成する。

```markdown
# ADR-XXX: Title

- **Status:** Proposed | Accepted | Superseded | Deprecated
- **Date:** YYYY-MM-DD
- **Category:** Principle | Domain | Architecture | Storage | API | Security | AI
- **Decision Makers:** ...

## Context

背景と課題を記載する。

## Decision

採用した設計を記載する。

## Alternatives Considered

検討した代替案と採用しなかった理由を記載する。

## Consequences

### メリット

### デメリット

## Related Documents
```

---

# 7. ADRライフサイクル

ADRは以下の状態を持つ。

| Status     | 説明                |
| ---------- | ----------------- |
| Proposed   | 提案中               |
| Accepted   | 採用済み              |
| Superseded | 新しいADRによって置き換えられた |
| Deprecated | 非推奨               |

採用済みのADRを変更する場合は、原則として既存ADRを書き換えず、新しいADRを追加して変更理由を記録する。

---

# Revision History

| Version | Date       | Description     |
| ------- | ---------- | --------------- |
| 1.0     | 2026-06-30 | Initial version |
