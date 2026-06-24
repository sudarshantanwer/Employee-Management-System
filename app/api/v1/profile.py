"""Profile API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_profile_service
from app.models.user import UserInDB
from app.schemas.common import APIResponse
from app.schemas.employee import EmployeeProfileUpdateRequest
from app.schemas.profile import ProfileResponse
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "/me",
    response_model=APIResponse[ProfileResponse],
    summary="Get my profile",
)
async def get_my_profile(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> APIResponse[ProfileResponse]:
    """Get current user's profile with linked employee record."""
    result = await profile_service.get_profile(current_user)
    return APIResponse(success=True, message="Profile retrieved successfully", data=result)


@router.put(
    "/me",
    response_model=APIResponse[ProfileResponse],
    summary="Update my profile",
)
async def update_my_profile(
    data: EmployeeProfileUpdateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> APIResponse[ProfileResponse]:
    """Update self-service profile fields."""
    result = await profile_service.update_profile(data, current_user)
    return APIResponse(success=True, message="Profile updated successfully", data=result)
