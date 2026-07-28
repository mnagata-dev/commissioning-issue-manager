"""Authentication API routes."""

from fastapi import APIRouter, Request

from app.api.deps import AuthServiceDependency, CurrentUserDependency
from app.schemas import CurrentUserResponse, LoginRequest

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login")
def login(
    request: Request,
    credentials: LoginRequest,
    auth_service: AuthServiceDependency,
) -> dict[str, CurrentUserResponse]:
    """Authenticate credentials and create the HTTP session."""
    current_user = auth_service.login(credentials.username, credentials.password)
    request.session["user_id"] = current_user.id
    return {"user": current_user}


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: CurrentUserDependency) -> CurrentUserResponse:
    """Return the currently authenticated user."""
    return current_user


@router.post("/logout")
def logout(
    request: Request,
    current_user: CurrentUserDependency,
) -> dict[str, str]:
    """Clear the authenticated HTTP session."""
    del current_user
    request.session.clear()
    return {"message": "Logged out"}
