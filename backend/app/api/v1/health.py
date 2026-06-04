from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import error_envelope

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody


@router.get("/health/live", response_model=HealthResponse)
def health_live() -> HealthResponse:
    """Liveness probe: the process is up. Does not touch the database."""
    return HealthResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    responses={503: {"model": ErrorResponse, "description": "Database not ready"}},
)
def health_ready(db: Session = Depends(get_db)) -> Response:
    """Readiness probe: verify the database answers a trivial query.

    On failure returns a 503 error envelope with code ``not_ready``.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return error_envelope(
            code="not_ready",
            message="Service is not ready",
            status_code=503,
        )
    return HealthResponse(status="ok")
