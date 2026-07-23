"""Comment application service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Comment
from app.repositories import CommentRepository, IssueRepository, UserRepository
from app.schemas import CreateCommentRequest


class CommentService:
    def __init__(
        self,
        session: Session,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        comment_repository: CommentRepository,
    ) -> None:
        self.session = session
        self.issue_repository = issue_repository
        self.user_repository = user_repository
        self.comment_repository = comment_repository

    def create_comment(
        self, issue_id: int, request: CreateCommentRequest, user_id: int
    ) -> int:
        try:
            issue = self.issue_repository.find_by_id(issue_id)
            if issue is None:
                raise NotFoundError("Issue not found.")
            user = self.user_repository.find_by_id(user_id)
            if user is None:
                raise NotFoundError("User not found.")
            if request.comment == "":
                raise ValidationError("Comment must not be empty.")
            comment = Comment(
                issue=issue,
                creator=user,
                comment=request.comment,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            created = self.comment_repository.create(comment)
            self.session.commit()
            return created.id
        except Exception:
            self.session.rollback()
            raise
