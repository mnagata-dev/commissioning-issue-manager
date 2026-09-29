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

音声入力の文字起こしは Local Speech Recognition がローカル環境で行い、結果を Voice / Text Input に表示する。ユーザーは文字起こし結果を必要に応じて修正できるが、確認または修正を独立した必須操作とはしない。

ユーザーが Generate AI Draft を実行すると、AI は Voice / Text Input のテキスト（必要に応じて修正された文字起こし結果、またはユーザーが直接入力したテキスト）を解析する。AI は音声そのもの（raw audio）を解析しない。

AIが実施する機能は以下とする。

- Voice / Text Input のテキストの解析
- Categoryの推定
- 日本語のDescriptionの生成

AIが生成する情報は Category および Description のみとする。

AIは以下を実施しない。

- TargetTypeの決定
- Roomの決定
- Targetの決定
- Issue保存
- Issue更新
- Status変更
- Comment追加
- Attachment追加
- RoomMaster更新
- Project更新

AIが生成した Category および Description は「AI Draft」として表示し、ユーザーが確認し、必要に応じて修正した後に Issue として登録する。AI は Issue を自動登録しない。

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

- ユーザーによる AI Draft の Category および Description の確認操作が必須となる。
- 完全自動登録は行えない。

## Related Documents

- requirements/requirements_v1.0.md
- design/basic_design.md
