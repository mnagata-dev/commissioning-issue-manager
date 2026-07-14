# ADR-003: Category Definition

- **Status:** Accepted
- **Date:** 2026-06-30
- **Category:** Domain
- **Decision Makers:** Masato Nagata

## Context

Issueを分類するためのCategoryについて検討した。

当初は設備分類や原因分類など複数の案があったが、実際のコミッショニング業務では、ユーザーはまず「どの設備で問題が起きているか」を認識してIssueを登録する。

原因は調査後に判明することが多く、登録時点では未確定である。

## Decision

Categoryは**ユーザーが最初に認識した対象（一次対象）**を表すものとする。

Categoryは原因を表さない。

採用するCategoryは以下のとおりとする。

- LIGHTING
- SHADE
- KEYPAD
- SENSOR
- TSTAT
- PROCESSOR
- NETWORK
- SERVER
- INTEGRATION
- OTHER

## Alternatives Considered

### 原因分類

採用しなかった。

理由

- 登録時点では原因が不明な場合が多い。
- 調査が進むと原因が変わる可能性がある。
- Categoryが頻繁に変更される運用になる。

### 製品シリーズ分類

採用しなかった。

理由

- 将来Lutron以外の設備へ拡張しにくい。
- 利用者が迷いやすい。

## Consequences

### メリット

- 現場で直感的に入力できる。
- AIが推定しやすい。
- 集計結果が分かりやすい。
- 原因調査後もCategoryを変更する必要がない。

### デメリット

- 原因分析には別の情報（DescriptionやComment）が必要になる。

## Related Documents

- requirements/requirements_v1.0.md
- design/basic_design.md
- design/database_design.md
- ADR-002: TargetType Definition
