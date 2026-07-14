Commissioning Issue Manager (CIM) の実装フェーズを開始します。

まず、プロジェクトにアップロードされている最新版のドキュメントをすべて読み込み、設計内容を把握してください。

対象ドキュメント
- requirements.md
- basic_design.md
- database_design.md
- api_design.md
- ui_design.md
- detailed_design.md
- test_design.md
- project_conventions.md
- review_notes.md
- CHANGELOG.md

また、プロジェクト内の ADR (Architecture Decision Record) も読み込み、設計判断の経緯を把握してください。

【ドキュメントの優先順位】

以下の優先順位で設計内容を判断してください。

1. requirements.md
2. 各設計書
   - basic_design.md
   - database_design.md
   - api_design.md
   - ui_design.md
   - detailed_design.md
   - test_design.md
3. project_conventions.md
4. ADR
5. review_notes.md
6. CHANGELOG.md

最新版の Requirements および各設計書を正とします。

ADR は設計判断の経緯を理解するための資料です。ADR と最新版の設計書の内容が異なる場合は、最新版の設計書を優先してください。

【実装方針】

1. Requirements を最優先とし、最新版の各設計書を正として実装してください。

2. 設計書間で矛盾や不整合を見つけた場合は、実装を進める前に必ず指摘してください。

3. 設計変更が必要な場合は、勝手に実装を変更せず、必ず設計変更案を提示し、合意後に実装してください。

4. Requirements や設計書に記載のない仕様は推測して実装せず、必ず確認してください。

5. 実装は小さな単位で進めます。
   - 1機能 = 1ブランチ = 1Pull Request
   - レビューしやすい粒度を維持してください。

6. 各機能は以下の流れで進めます。
   - 実装方針の確認
   - 実装
   - テストコード作成
   - レビュー
   - コミット
   - Pull Request
   - マージ

7. テストコードは test_design.md に従って作成してください。

8. project_conventions.md の命名規則、ディレクトリ構成、コーディングルールに従ってください。

9. 実装中に改善案やリファクタリング案がある場合は歓迎します。ただし、設計変更を伴う場合は、必ず提案し、合意後に実装してください。

10. 品質・可読性・保守性を重視し、過度な最適化は行わないでください。

【ChatGPT と Codex の役割】

ChatGPT
- 実装方針の検討
- 設計レビュー
- アーキテクチャの相談
- コードレビュー
- リファクタリングの相談
- 不具合解析
- Git / GitHub 運用の相談

Codex
- コード実装
- ファイル作成・編集
- テストコード作成
- リファクタリング
- 小さな単位での実装

【レビュー方針】

実装前に、対象機能について設計書との整合性を確認してください。

実装後は、Requirements、各設計書、および test_design.md との整合性を確認し、必要に応じて改善点を提案してください。

ただし、設計変更を伴う場合は、勝手に実装を変更せず、必ず提案してください。

まずは最新版の設計書をすべて読み込み、設計内容を要約した上で、実装フェーズ全体の進め方を提案してください。その後は、一つの機能ごとに「設計確認 → 実装 → テスト → レビュー → コミット → Pull Request」の流れで進めます。
