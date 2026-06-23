"""Health check endpoints."""

from fastapi import APIRouter

from app.core.database import db_manager
from app.core.redis import redis_manager
from app.schemas.common import APIResponse, HealthResponse, HealthStatus

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    summary="Health check",
    description="Returns application, MongoDB, and Redis health status.",
)
async def health_check() -> APIResponse[HealthResponse]:
    """Check health of all system components."""
    mongo_health = await db_manager.health_check()
    redis_health = await redis_manager.health_check()

    app_healthy = True
    application = HealthStatus(status="running", healthy=app_healthy)

    mongodb = HealthStatus(
        status=mongo_health.get("status", "unknown"),
        healthy=mongo_health.get("healthy", False),
        detail=mongo_health.get("detail"),
    )

    redis_status = HealthStatus(
        status=redis_health.get("status", "unknown"),
        healthy=redis_health.get("healthy", False),
        detail=redis_health.get("detail"),
    )

    return APIResponse(
        success=True,
        message="Health check completed",
        data=HealthResponse(
            application=application,
            mongodb=mongodb,
            redis=redis_status,
        ),
    )
