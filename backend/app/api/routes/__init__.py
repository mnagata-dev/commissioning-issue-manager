"""API route modules."""

from app.api.routes.auth import router as auth_router
from app.api.routes.issues import router as issues_router
from app.api.routes.projects import router as projects_router

__all__ = ["auth_router", "issues_router", "projects_router"]
