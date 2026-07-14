# ADR-005: Issue as Aggregate Root

- **Status:** Accepted
- **Date:** 2026-06-30
- **Category:** Domain
- **Decision Makers:** Masato Nagata

## Context

Issue、Comment、Attachmentの関係について検討した。

CommentやAttachmentは単独で管理するものではなく、必ずIssueに関連付けられる。

業務上も、コミッショニングの管理単位はIssueである。

## Decision

Issueを集約ルート（Aggregate Root）とする。

CommentおよびAttachmentはIssueに属する子エンティティとする。

CommentおよびAttachmentはIssueを介してのみ操作する。

APIは以下の構成とする。

- `POST /api/issues/{issue_id}/comments`
- `POST /api/issues/{issue_id}/attachments`
- `DELETE /api/issues/{issue_id}/attachments/{attachment_id}`

Comment一覧およびAttachment一覧はIssue Detail APIのレスポンスに含める。

## Alternatives Considered

### Commentを独立リソースとする

採用しなかった。

理由

- 業務上、Commentだけを操作する場面がない。
- APIが複雑になる。

### Attachmentを独立リソースとする

採用しなかった。

理由

- 必ずIssueに属するため独立性がない。
- URL設計が分かりにくくなる。

## Consequences

### メリット

- REST APIが自然な構成になる。
- ドメインモデルが分かりやすい。
- Issue中心の業務フローと一致する。

### デメリット

- CommentやAttachmentを単独で扱う場合はIssue経由のアクセスが必要となる。

## Related Documents

- requirements/requirements_v1.0.md
- design/basic_design.md
- design/api_design.md
- design/database_design.md
