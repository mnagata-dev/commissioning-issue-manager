# ADR-006: Local Speech Recognition Technology

* **Status:** Accepted
* **Date:** 2026-09-30
* **Category:** Technology
* **Decision Makers:** Masato Nagata

## Context

CIMでは、音声入力をローカル環境で文字起こしし、その結果を Voice / Text Input に表示する。

要件および設計では、音声認識はインターネット接続や外部クラウドサービスを前提とせず、Local Speech Recognition として実行する方針としている。

一方、Local Speech Recognition に使用する具体的な技術は未決定であった。

初期版で使用する技術を選定するため、whisper.cpp を使用した Proof of Concept (PoC) を実施した。

PoCでは以下を確認した。

* ローカル環境で音声認識を実行できる。
* 日本語音声を文字起こしできる。
* CPUのみの環境で実行できる。
* Pythonからwhisper.cppのCLIを実行できる。
* 文字起こし結果をPythonの文字列として取得できる。

また、音声によっては誤認識が発生することも確認した。

CIMでは文字起こし結果を Voice / Text Input に表示し、ユーザーが必要に応じて修正できるため、音声認識結果をそのまま業務データとして確定しない。

## Decision

CIMの初期版における Local Speech Recognition の実装技術として **whisper.cpp** を採用する。

Backendからwhisper.cppへのアクセスは、音声認識技術への依存を分離できる境界を介して行う。

Local Speech Recognition は音声をテキストへ変換する責務のみを持ち、AI Draft の生成および業務データの登録・更新は行わない。

使用するWhisperモデル、実行ファイルおよびモデルの配置、一時ファイルの扱い、入力音声形式、音声変換方法、タイムアウトなどの具体的な実装詳細は、本ADRでは決定しない。

## Alternatives Considered

### クラウド音声認識サービス

採用しなかった。

理由

* CIMはインターネット接続を前提としない。
* 外部クラウドサービスへの依存を避ける必要がある。

### ブラウザ提供の音声認識機能

採用しなかった。

理由

* ブラウザおよび実行環境への依存が大きい。
* CIMが要求するローカル・オフライン動作を一貫して保証しにくい。

## Consequences

### メリット

* 音声認識をローカル環境で実行できる。
* 外部クラウドサービスに依存しない。
* Python Backendから音声認識を利用できる。
* 音声認識技術への依存を境界の内側に閉じ込められる。

### デメリット

* whisper.cppの実行環境およびモデルをローカルに用意する必要がある。
* 音声認識結果には誤認識が含まれる可能性がある。
* 実行ファイル、モデル、音声データなどのローカルリソース管理が必要になる。

## Related Documents

* requirements/requirements.md
* design/basic_design.md
* design/api_design.md
* design/ui_design.md
* design/detailed_design.md
* design/test_design.md
* ADR-001: User in Control
