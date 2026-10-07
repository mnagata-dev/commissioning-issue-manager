# ADR-007: Target Type Simplification

- **Status:** Accepted
- **Date:** 2026-10-07
- **Category:** Domain
- **Decision Makers:** Masato Nagata

## Context

ADR-002 は、Target Type を ROOM / ROOM_TYPE / AREA / HOTEL / GENERAL の5種類とする過去の決定を記録している。

その後、Requirements v1.2 で初期版の Target Type は ROOM / OTHER に整理され、旧4種類の削除が CHANGELOG に記録された。現行 Requirements v1.3 および関連設計書も、この2種類を定義している。

本 ADR は、すでに Requirements / 設計書で採用されている変更を意思決定履歴として記録する。新しい仕様は追加しない。Date は本 ADR の記録日であり、過去の変更の承認日を示さない。

## Decision

初期版の Target Type は ROOM / OTHER の2種類とする。

### ROOM

- 客室を対象とする。
- Room はユーザーが選択する。
- `room_id` は必須とする。
- `target` は null とする。

### OTHER

- Room 以外の対象を表す。
- Target はユーザーが自由入力する。
- `room_id` は null とする。
- `target` は必須とする。

Target Type / Room / Target はユーザーが決定する。AI はこれらを決定・推測しない。

本 ADR は ADR-002 の旧5種類の Target Type decision を supersede する。ADR-002 の歴史的な本文は保持する。

## Alternatives Considered

### ADR-002 の旧5種類を現行仕様として維持する

現行 Requirements / 設計書の ROOM / OTHER 定義と矛盾するため採用しない。本項は、過去の検討経緯や承認理由を推測して記録するものではない。

## Consequences

### メリット

- 現行 Requirements / 設計書と ADR の適用関係が明確になる。
- 過去の意思決定本文を保持したまま、現行の Target Type 定義を参照できる。

### デメリット

- 過去の決定を参照する場合は、ADR-002 と本 ADR の後継関係を確認する必要がある。

## Related Documents

- [Requirements v1.3: 7.5 / 9.9 Target Type](../requirements/requirements.md)
- [Requirements CHANGELOG: Version 1.2](../requirements/CHANGELOG.md)
- [Basic Design](../design/basic_design.md)
- [Database Design](../design/database_design.md)
- [API Design](../design/api_design.md)
- [UI Design](../design/ui_design.md)
- [Detailed Design](../design/detailed_design.md)
- [Test Design](../design/test_design.md)
- [ADR-001: User in Control](ADR-001-user-in-control.md)
- [ADR-002: TargetType Definition](ADR-002-target-type-definition.md)
