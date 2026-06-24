"""Analytics API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_analytics_service
from app.models.user import UserInDB
from app.schemas.analytics import DashboardAnalytics
from app.schemas.common import APIResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=APIResponse[DashboardAnalytics],
    summary="Dashboard analytics",
)
async def get_dashboard_analytics(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> APIResponse[DashboardAnalytics]:
    """Get aggregated dashboard metrics."""
    result = await analytics_service.get_dashboard_analytics(current_user)
    return APIResponse(success=True, message="Analytics retrieved successfully", data=result)
