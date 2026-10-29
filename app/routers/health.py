"""
Health check router for monitoring service status, version, and database connectivity.
Follows Cloud-native health check patterns (RFC draft / standard REST practice).
"""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from app.config import get_settings
from app.database import check_db_connection
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns service availability, application version, current UTC timestamp, and database connectivity status.",
    responses={
        200: {
            "description": "Service is operational and database connection is verified.",
            "model": HealthResponse,
        }
    },
)
def get_health() -> HealthResponse:
    """Check application health and database connection."""
    db_ok = check_db_connection()
    db_status = "connected" if db_ok else "unreachable"

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        database=db_status,
    )
