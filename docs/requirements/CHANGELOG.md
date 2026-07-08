# Requirements Change Log

**Document:** requirements.md

---

# Purpose

本書は、`requirements.md` の変更履歴を管理することを目的とする。

要件の追加・変更・削除について、変更内容および理由を記録する。

設計書や実装の変更履歴は本書の対象外とする。

---

# Version History

|Version|Date|Description|
|---|---|---|
|1.0|2026-06-30|Initial version|
|1.1|2026-07-03|Reflect reviewed requirements changes|

---

# Change Records

## Version 1.0

### Added

初版作成。

以下の要件を定義した。

- User Authentication
- Project Management（CLI / CSV）
- Project Selection
- RoomType
- Room
- Issue Management
- Comment Management
- Attachment Management
- AI Draft
- Local File Storage

---

### Changed

なし

---

### Removed

なし

---

## Version 1.1

### Added

- Hotel を Master Data に追加した。
- User に password_hash を追加した。
- username をログイン ID とし、メールアドレス形式も許容する要件を追加した。

---

### Changed

- Master Data の構成を見直した。
- Administrator の責務を整理した。

---

### Removed

- Hotel Code の管理要件を削除した。
- Project Code の管理要件を削除した。
- RoomType Code の管理要件を削除した。
- RoomType の description 管理要件を削除した。

---

# Change Policy

変更履歴は、`requirements.md` に対して以下の変更が発生した場合に更新する。

- 要件追加
- 要件変更
- 要件削除
- 要件の大幅な見直し

軽微な誤字・表現修正のみの場合は更新対象としない。

---

# Version Numbering

以下のルールで管理する。

|Version|内容|
|---|---|
|Major|要件の大幅変更|
|Minor|要件追加・変更|
|Patch|軽微な修正（通常は本書へ記録しない）|

例

```text id="x6rn77"
1.0

1.1

1.2

2.0
```

---

# Notes

本書は `requirements.md` の変更履歴のみを管理する。

設計変更についてはADR（Architecture Decision Record）およびGitのコミット履歴で管理する。
