"""Comment API routes."""

from fastapi import APIRouter

from app.api.deps import CommentServiceDependency, CurrentUserDependency
from app.schemas import CommentResponse, CreateCommentRequest

router = APIRouter(prefix="/api/issues", tags=["comments"])


@router.post("/{issue_id}/comments")
def create_comment(
    issue_id: int,
    request: CreateCommentRequest,
    current_user: CurrentUserDependency,
    comment_service: CommentServiceDependency,
) -> dict[str, int | str]:
    comment_id = comment_service.create_comment(
        issue_id=issue_id,
        request=request,
        user_id=current_user.id,
    )
    return {"id": comment_id, "message": "Comment created"}


@router.get("/{issue_id}/comments")
def list_comments(
    issue_id: int,
    current_user: CurrentUserDependency,
    comment_service: CommentServiceDependency,
) -> dict[str, list[CommentResponse]]:
    del current_user
    return {"items": comment_service.list_comments(issue_id)}
