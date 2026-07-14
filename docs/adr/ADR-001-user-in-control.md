# ADR-001: User in Control

- **Status:** Accepted
- **Date:** 2026-06-30
- **Category:** Principle
- **Decision Makers:** Masato Nagata

## Context

CIMでは音声入力とローカルLLM（Ollama）を利用してIssue登録を支援する。

AIは入力負担を大幅に軽減できる一方、誤認識や誤分類を完全に防ぐことはできない。

コミッショニング業務では、誤ったIssue登録やStatus変更が現場に大きな影響を与えるため、AIへ業務判断を委ねることは適切ではない。

## Decision

AIは補助機能として利用し、業務データの最終決定は必ずユーザーが行う。

AIが実施する機能は以下とする。

- 音声入力内容の解析
- Categoryの推定
- Descriptionの生成

AIは以下を実施しない。

- TargetTypeの決定
- Targetの決定
- Issue保存
- Issue更新
- Status変更
- Comment追加
- Attachment追加
- RoomMaster更新
- Project更新

AIが生成した Category および Description は「AI Draft」として表示し、ユーザーが確認・修正した後に Issue として保存する。

## Alternatives Considered

### AIによる完全自動登録

採用しなかった。

理由

- 誤登録のリスクが高い。
- コミッショニング業務では最終判断は人が行うべきである。

## Consequences

### メリット

- 誤登録を防止できる。
- AIモデルを変更しても業務ルールが変わらない。
- 利用者が安心してAIを利用できる。
- AIは入力支援に集中できる。

### デメリット

- ユーザーによる確認操作が必須となる。
- 完全自動登録は行えない。

## Related Documents

- requirements/requirements_v1.0.md
- design/basic_design.md
