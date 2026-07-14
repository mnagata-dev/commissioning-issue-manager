# Requirements Review Notes

**Document:** requirements.md

---

# Purpose

本書は、`requirements.md` のレビュー記録を管理することを目的とする。

レビュー時に確認した内容、指摘事項、対応結果および保留事項を記録する。

設計レビューやコードレビューは本書の対象外とする。

---

# Review Policy

Requirements Reviewでは以下を確認する。

- 要件漏れがないこと
- 要件間で矛盾がないこと
- 実現可能な要件であること
- 初期版のスコープが適切であること

---

# Review Records

## Review No.1

**Date**

2026-06-30

**Reviewer**

Masato Nagata

### Review Result

Accepted

### Confirmed Items

以下の内容を確認した。

- Project単位でIssueを管理すること
- RoomおよびRoomTypeを採用すること
- Issueを中心とした業務モデルとすること
- AIはIssue Draft生成のみを担当すること
- Userが最終確認を行うこと(User in Control)
- AttachmentはLocal Storageへ保存すること
- 管理データ(Project・Room・RoomType・User)はCLIまたはCSVで管理すること
- 初期版ではWeb管理画面を提供しないこと

### Issues

なし

### Action Items

なし

---

## Review No.2

**Date**

2026-07-03

**Reviewer**

Masato Nagata

### Review Result

Accepted

### Confirmed Items

以下の内容を確認した。

- Hotel を Master Data に追加すること
- User に password_hash を追加すること
- username をログイン ID とし、メールアドレス形式も許容すること
- Hotel Code、Project Code および RoomType Code を廃止すること
- RoomType.description を廃止すること
- requirements.md と関連設計書の整合性を確認し、更新すること

### Issues

なし

### Action Items

なし

---

## Review No.3

**Date**

2026-07-08

**Reviewer**

Masato Nagata

### Review Result

Accepted

### Confirmed Items

以下の内容を確認した。

- Requirements を最上位ドキュメントとして再整理したこと
- ドキュメントの目的および利用シナリオを明確化したこと
- Document Principles を追加したこと
- Typical Workflow を追加したこと
- Design Principles を追加したこと
- Room は Hotel に属すること
- Project は Hotel に属する案件であること
- Issue が Project と対象を結び付けること
- Target Type を ROOM および OTHER に整理したこと
- 初期版では Location を採用しないこと
- AI は Category および Description の AI Draft のみを生成すること
- AI は Room、Target Type および Target を決定しないこと
- Administrator は Engineer のすべての機能を利用できること
- requirements.md と関連設計書の整合性を確認し、更新すること

### Issues

なし

### Action Items

- basic_design.md 以降の設計書を Requirements Version 1.2 に合わせて更新すること

---

# Open Items

現時点で未解決の要件はない。

今後、新たな業務要件が発生した場合は、本書へレビュー結果を追記したうえで、`requirements.md` および必要に応じて関連設計書を更新する。

---

# Review Procedure

Requirements変更時は、以下の手順でレビューを実施する。

1. `requirements.md` を更新する。
2. `CHANGELOG.md` を更新する。
3. 本書へレビュー結果を記録する。
4. 要件変更が設計へ影響する場合は、関連する設計書を更新する。
5. アーキテクチャに関する重要な判断を行った場合は、新しいADRを追加する。

---

# Notes

本書は `requirements.md` のレビュー履歴のみを管理する。

基本設計以降のレビューは、それぞれの設計書またはADR、Gitのコミット履歴で管理する。
