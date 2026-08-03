"""Project API routes."""

from fastapi import APIRouter

from app.api.deps import (
    CurrentUserDependency,
    IssueServiceDependency,
    ProjectServiceDependency,
)
from app.schemas import CreateIssueRequest, IssueListResponse, ProjectListResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    current_user: CurrentUserDependency,
    project_service: ProjectServiceDependency,
) -> ProjectListResponse:
    return project_service.list_projects(current_user.id)


@router.get("/{project_id}/issues", response_model=IssueListResponse)
def list_issues(
    project_id: int,
    current_user: CurrentUserDependency,
    issue_service: IssueServiceDependency,
    status: str | None = None,
    category: str | None = None,
    target_type: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> IssueListResponse:
    del current_user
    return issue_service.list_issues(
        project_id, status, category, target_type, keyword, page, page_size
    )


@router.post("/{project_id}/issues")
def create_issue(
    project_id: int,
    request: CreateIssueRequest,
    current_user: CurrentUserDependency,
    issue_service: IssueServiceDependency,
) -> dict[str, int | str]:
    issue_id = issue_service.create_issue(
        project_id=project_id,
        request=request,
        user_id=current_user.id,
    )
    return {"id": issue_id, "message": "Issue created"}
