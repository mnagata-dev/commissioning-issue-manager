"""Comment application service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Comment, Issue, User
from app.repositories import CommentRepository, IssueRepository, UserRepository
from app.schemas import CommentResponse, CreateCommentRequest


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
            issue = self._require_issue(issue_id)
            user = self._require_user(user_id)
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

    def list_comments(self, issue_id: int) -> list[CommentResponse]:
        self._require_issue(issue_id)
        comments = self.comment_repository.list_by_issue(issue_id)
        return [
            CommentResponse(
                id=comment.id,
                comment=comment.comment,
                created_by={
                    "id": comment.creator.id,
                    "display_name": comment.creator.display_name,
                },
                created_at=comment.created_at,
            )
            for comment in comments
        ]

    def _require_issue(self, issue_id: int) -> Issue:
        issue = self.issue_repository.find_by_id(issue_id)
        if issue is None:
            raise NotFoundError("Issue not found.")
        return issue

    def _require_user(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user
