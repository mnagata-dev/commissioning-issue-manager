"""Comment database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Comment


class CommentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_issue(self, issue_id: int) -> list[Comment]:
        statement = (
            select(Comment)
            .where(Comment.issue_id == issue_id)
            .order_by(Comment.created_at.asc(), Comment.id.asc())
        )
        return list(self.session.scalars(statement))

    def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        self.session.flush()
        return comment
