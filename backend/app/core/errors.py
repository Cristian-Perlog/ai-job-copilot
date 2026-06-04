import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import request_id_var

logger = logging.getLogger("app.errors")


def error_envelope(code: str, message: str, status_code: int) -> JSONResponse:
    """Build the standard error response body.

    Shape: {"error": {"code", "message", "request_id"}}.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id_var.get() or "",
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Wrap HTTPException in the standard envelope, preserving status code."""
    message = exc.detail if isinstance(exc.detail, str) else "Error"
    return error_envelope(
        code=f"http_{exc.status_code}",
        message=message,
        status_code=exc.status_code,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a generic 500 envelope and log the stack trace.

    Exception details are never leaked to the client.
    """
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return error_envelope(
        code="internal_error",
        message="Internal server error",
        status_code=500,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
