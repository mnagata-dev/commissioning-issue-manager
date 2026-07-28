"""FastAPI application entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth_router
from app.core.config import Settings, settings
from app.core.exceptions import ApplicationError

logger = logging.getLogger(__name__)


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
    application.include_router(auth_router)
    return application


app = create_app()
