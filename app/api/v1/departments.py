"""Department API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_department_service
from app.models.user import UserInDB
from app.schemas.common import APIResponse
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get(
    "",
    response_model=APIResponse[list[DepartmentResponse]],
    summary="List departments",
)
async def list_departments(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    department_service: Annotated[DepartmentService, Depends(get_department_service)],
) -> APIResponse[list[DepartmentResponse]]:
    """List all departments."""
    result = await department_service.list_departments(current_user)
    return APIResponse(success=True, message="Departments retrieved successfully", data=result)


@router.get(
    "/{department_id}",
    response_model=APIResponse[DepartmentResponse],
    summary="Get department by ID",
)
async def get_department(
    department_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    department_service: Annotated[DepartmentService, Depends(get_department_service)],
) -> APIResponse[DepartmentResponse]:
    """Get department details."""
    result = await department_service.get_department(department_id, current_user)
    return APIResponse(success=True, message="Department retrieved successfully", data=result)


@router.post(
    "",
    response_model=APIResponse[DepartmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
)
async def create_department(
    data: DepartmentCreateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    department_service: Annotated[DepartmentService, Depends(get_department_service)],
) -> APIResponse[DepartmentResponse]:
    """Create a new department. Admin only."""
    result = await department_service.create_department(data, current_user)
    return APIResponse(success=True, message="Department created successfully", data=result)


@router.put(
    "/{department_id}",
    response_model=APIResponse[DepartmentResponse],
    summary="Update department",
)
async def update_department(
    department_id: str,
    data: DepartmentUpdateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    department_service: Annotated[DepartmentService, Depends(get_department_service)],
) -> APIResponse[DepartmentResponse]:
    """Update a department. Admin only."""
    result = await department_service.update_department(department_id, data, current_user)
    return APIResponse(success=True, message="Department updated successfully", data=result)


@router.delete(
    "/{department_id}",
    response_model=APIResponse[DepartmentResponse],
    summary="Delete department",
)
async def delete_department(
    department_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    department_service: Annotated[DepartmentService, Depends(get_department_service)],
) -> APIResponse[DepartmentResponse]:
    """Soft delete a department. Admin only."""
    result = await department_service.delete_department(department_id, current_user)
    return APIResponse(success=True, message="Department deleted successfully", data=result)
