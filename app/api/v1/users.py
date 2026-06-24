"""User management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_user_service
from app.models.user import UserInDB
from app.schemas.common import APIResponse, PaginatedData
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[UserResponse]],
    summary="List users",
)
async def list_users(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query()] = None,
    role: Annotated[str | None, Query()] = None,
) -> APIResponse[PaginatedData[UserResponse]]:
    """List users. Admin only."""
    result = await user_service.list_users(
        current_user, page=page, limit=limit, search=search, role=role
    )
    return APIResponse(success=True, message="Users retrieved successfully", data=result)


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="Get user by ID",
)
async def get_user(
    user_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """Get user details. Admin only."""
    result = await user_service.get_user(user_id, current_user)
    return APIResponse(success=True, message="User retrieved successfully", data=result)


@router.put(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="Update user",
)
async def update_user(
    user_id: str,
    data: UserUpdateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> APIResponse[UserResponse]:
    """Update user role, employee link, or status. Admin only."""
    result = await user_service.update_user(user_id, data, current_user)
    return APIResponse(success=True, message="User updated successfully", data=result)
