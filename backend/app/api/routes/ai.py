"""AI Draft API routes."""

from fastapi import APIRouter

from app.api.deps import AIServiceDependency, CurrentUserDependency
from app.schemas import GenerateDraftRequest, GenerateDraftResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/issue-draft", response_model=GenerateDraftResponse)
def generate_issue_draft(
    request: GenerateDraftRequest,
    current_user: CurrentUserDependency,
    ai_service: AIServiceDependency,
) -> GenerateDraftResponse:
    return ai_service.generate_issue_draft(
        request=request,
        user_id=current_user.id,
    )
