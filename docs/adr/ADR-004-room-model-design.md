# ADR-004: Room Model Design

* **Status:** Accepted
* **Date:** 2026-06-30
* **Category:** Domain
* **Decision Makers:** Masato Nagata

## Context

Roomモデルの構造について検討した。

当初はRoomへfloor_numberやhotel_idを保持する案もあったが、業務フローを整理した結果、必要最小限の構成を採用する方針となった。

また、フロア単位のIssueはTargetType = AREAで表現することとした。

## Decision

Roomは以下の情報のみを管理する。

* Room Number
* RoomType

RoomはRoomTypeを参照する。

Roomはfloor_numberを保持しない。

Room Numberの重複チェックはService層で行う。

## Alternatives Considered

### Roomへfloor_numberを保持する

採用しなかった。

理由

* フロア情報はIssue管理には必須ではない。
* AREAで十分表現できる。
* モデルを簡潔に保てる。

### Roomへhotel_idを保持する

採用しなかった。

理由

* RoomTypeからHotelを取得できる。
* データの重複を避けられる。
* アプリケーション側で整合性を検証する設計とした。

## Consequences

### メリット

* Roomモデルがシンプルになる。
* 保守性が向上する。
* 将来RoomTypeの変更にも対応しやすい。

### デメリット

* Hotelとの整合性はService層で検証する必要がある。

## Related Documents

* requirements/requirements_v1.0.md
* design/database_design.md
* ADR-002: TargetType Definition
