"""FastAPI application entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(title=settings.application_name, debug=settings.debug)
    application.add_exception_handler(ApplicationError, application_error_handler)
    return application


app = create_app()
