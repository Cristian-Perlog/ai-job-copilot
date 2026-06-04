import logging
from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import request_id_var
from app.core.middleware import REQUEST_ID_HEADER

logger = logging.getLogger("app.errors")


def error_envelope(
    code: str,
    message: str,
    status_code: int,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build the standard error response body.

    Shape: {"error": {"code", "message", "request_id"}}.

    ``headers`` are forwarded onto the response (e.g. WWW-Authenticate for
    401 challenges, Retry-After for 429).
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
        headers=dict(headers) if headers else None,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Wrap HTTPException in the standard envelope, preserving status code.

    ``exc.headers`` is forwarded so auth challenges (WWW-Authenticate) and
    rate-limit hints (Retry-After) survive the envelope wrapping.
    """
    message = exc.detail if isinstance(exc.detail, str) else "Error"
    return error_envelope(
        code=f"http_{exc.status_code}",
        message=message,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a generic 500 envelope and log the stack trace.

    Exception details are never leaked to the client.

    A handler registered for bare ``Exception`` is hoisted by Starlette into
    ``ServerErrorMiddleware`` -- the outermost layer, above CORSMiddleware and
    RequestIDMiddleware -- so its response bypasses both. We therefore set the
    X-Request-ID and CORS headers here by hand, mirroring CORSMiddleware
    semantics (echo the configured origin only when it matches), so the
    cross-origin frontend can read the error envelope and correlate the request.
    """
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)

    headers: dict[str, str] = {REQUEST_ID_HEADER: request_id_var.get() or ""}

    origin = request.headers.get("origin")
    if origin and origin == settings.frontend_origin:
        headers["Access-Control-Allow-Origin"] = settings.frontend_origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Vary"] = "Origin"

    return error_envelope(
        code="internal_error",
        message="Internal server error",
        status_code=500,
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
