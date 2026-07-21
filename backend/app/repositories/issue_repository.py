"""Issue database access."""

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Issue


class IssueRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, issue_id: int) -> Issue | None:
        return self.session.get(Issue, issue_id)

    def list_by_project(
        self,
        project_id: int,
        status: str | None,
        category: str | None,
        target_type: str | None,
        keyword: str | None,
        offset: int,
        limit: int,
    ) -> list[Issue]:
        statement = self._filtered_statement(
            select(Issue), project_id, status, category, target_type, keyword
        )
        statement = statement.order_by(
            Issue.updated_at.desc(), Issue.id.desc()
        ).offset(offset).limit(limit)
        return list(self.session.scalars(statement))

    def count_by_project(
        self,
        project_id: int,
        status: str | None,
        category: str | None,
        target_type: str | None,
        keyword: str | None,
    ) -> int:
        statement = self._filtered_statement(
            select(func.count(Issue.id)),
            project_id,
            status,
            category,
            target_type,
            keyword,
        )
        return self.session.scalar(statement) or 0

    def create(self, issue: Issue) -> Issue:
        self.session.add(issue)
        self.session.flush()
        return issue

    def update(self, issue: Issue) -> Issue:
        self.session.flush()
        return issue

    @staticmethod
    def _filtered_statement(
        statement: Select[Any],
        project_id: int,
        status: str | None,
        category: str | None,
        target_type: str | None,
        keyword: str | None,
    ) -> Select[Any]:
        statement = statement.where(Issue.project_id == project_id)
        if status is not None:
            statement = statement.where(Issue.status == status)
        if category is not None:
            statement = statement.where(Issue.category == category)
        if target_type is not None:
            statement = statement.where(Issue.target_type == target_type)
        if keyword is not None:
            statement = statement.where(Issue.description.contains(keyword))
        return statement
