# ADR-002: TargetType Definition

* **Status:** Accepted
* **Date:** 2026-06-30
* **Category:** Domain
* **Decision Makers:** Masato Nagata

## Context

Issueがどこを対象としているかを表現する方法を検討した。

当初は以下のTargetTypeを候補としていた。

* ROOM
* ROOM_TYPE
* FLOOR
* AREA
* HOTEL
* GENERAL

設計を進める中で、FLOORはAREAで十分に表現できることが分かった。

また、Roomモデルからもfloor_numberを削除する方針となった。

## Decision

TargetTypeは以下の5種類とする。

* ROOM
* ROOM_TYPE
* AREA
* HOTEL
* GENERAL

各TargetTypeの意味は以下のとおりとする。

| TargetType | 説明                                          |
| ---------- | ------------------------------------------- |
| ROOM       | 特定の客室                                       |
| ROOM_TYPE  | 客室タイプ全体                                     |
| AREA       | ホテル内の任意の場所（Lobby、Back Office、3F Corridorなど） |
| HOTEL      | ホテル全体                                       |
| GENERAL    | 対象が未確定、またはホテル全体にも属さない一般事項                   |

TargetTypeはIssueが「どこで発生したか」を表す。

設備の種類はCategoryで表現する。

## Alternatives Considered

### FLOORを残す案

採用しなかった。

理由

* AREAで表現可能である。
* TargetTypeが増え、判定ロジックが複雑になる。
* Roomモデルとの整合性が取りにくい。

## Consequences

### メリット

* TargetTypeを5種類に整理できる。
* AIによる分類が簡潔になる。
* UIが分かりやすくなる。
* 将来の拡張もしやすい。

### デメリット

* フロア単位のIssueはAREAとして入力する運用となる。

## Related Documents

* requirements/requirements_v1.0.md
* design/basic_design.md
* design/database_design.md
