from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import error_envelope

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health/live", response_model=HealthResponse)
def health_live() -> HealthResponse:
    """Liveness probe: the process is up. Does not touch the database."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
def health_ready(db: Session = Depends(get_db)):
    """Readiness probe: verify the database answers a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return error_envelope(
            code="not_ready",
            message="Service is not ready",
            status_code=503,
        )
    return HealthResponse(status="ok")
