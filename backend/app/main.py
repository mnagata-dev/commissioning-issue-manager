"""FastAPI application entry point."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import (
    ai_router,
    attachments_router,
    auth_router,
    comments_router,
    issues_router,
    projects_router,
)
from app.core.config import Settings, settings
from app.core.exceptions import ApplicationError, ValidationError

logger = logging.getLogger(__name__)

FRONTEND_DIRECTORY = Path(__file__).resolve().parents[2] / "frontend"


async def application_error_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    """Convert an application error to the common API response."""
    del request
    if not isinstance(exception, ApplicationError):
        raise TypeError("Expected ApplicationError")
    logger.warning("Application error: %s", exception.code)
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": {"code": exception.code, "message": exception.message}},
    )


async def request_validation_error_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    """Convert request validation failures to the common safe response."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("Expected RequestValidationError")
    return await application_error_handler(request, ValidationError())


def create_app(application_settings: Settings = settings) -> FastAPI:
    """Create and configure the FastAPI application."""
    if not application_settings.session_secret:
        raise RuntimeError("CIM_SESSION_SECRET must be configured")

    application = FastAPI(
        title=application_settings.application_name,
        debug=application_settings.debug,
    )
    application.add_middleware(
        SessionMiddleware,
        secret_key=application_settings.session_secret,
        session_cookie="cim_session",
        max_age=28800,
        same_site="lax",
        https_only=False,
        path="/",
    )
    application.add_exception_handler(ApplicationError, application_error_handler)
    application.add_exception_handler(
        RequestValidationError,
        request_validation_error_handler,
    )
    application.include_router(auth_router)
    application.include_router(projects_router)
    application.include_router(issues_router)
    application.include_router(comments_router)
    application.include_router(attachments_router)
    application.include_router(ai_router)

    @application.get("/", include_in_schema=False)
    def login_page() -> FileResponse:
        """Return the Login page."""
        return FileResponse(FRONTEND_DIRECTORY / "index.html")

    @application.get("/projects.html", include_in_schema=False)
    def projects_page() -> FileResponse:
        """Return the Project Selection page."""
        return FileResponse(FRONTEND_DIRECTORY / "projects.html")

    @application.get("/issues.html", include_in_schema=False)
    def issues_page() -> FileResponse:
        """Return the Issue List page."""
        return FileResponse(FRONTEND_DIRECTORY / "issues.html")

    application.mount(
        "/css",
        StaticFiles(directory=FRONTEND_DIRECTORY / "css"),
        name="frontend-css",
    )
    application.mount(
        "/js",
        StaticFiles(directory=FRONTEND_DIRECTORY / "js"),
        name="frontend-js",
    )
    return application


app = create_app()
