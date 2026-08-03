"""Issue API routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUserDependency, IssueServiceDependency
from app.schemas import (
    IssueDetailResponse,
    UpdateIssueRequest,
    UpdateIssueStatusRequest,
)

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/{issue_id}", response_model=IssueDetailResponse)
def get_issue_detail(
    issue_id: int,
    current_user: CurrentUserDependency,
    issue_service: IssueServiceDependency,
) -> IssueDetailResponse:
    del current_user
    return issue_service.get_issue_detail(issue_id)


@router.put("/{issue_id}")
def update_issue(
    issue_id: int,
    request: UpdateIssueRequest,
    current_user: CurrentUserDependency,
    issue_service: IssueServiceDependency,
) -> dict[str, int | str]:
    issue_service.update_issue(
        issue_id=issue_id,
        request=request,
        user_id=current_user.id,
    )
    return {"id": issue_id, "message": "Issue updated"}


@router.patch("/{issue_id}/status")
def update_issue_status(
    issue_id: int,
    request: UpdateIssueStatusRequest,
    current_user: CurrentUserDependency,
    issue_service: IssueServiceDependency,
) -> dict[str, int | str]:
    issue_service.update_status(
        issue_id=issue_id,
        request=request,
        user_id=current_user.id,
    )
    return {"id": issue_id, "status": request.status, "message": "Status updated"}
