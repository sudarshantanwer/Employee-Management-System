"""Employee API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import PlainTextResponse

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_employee_service
from app.models.user import UserInDB
from app.schemas.common import APIResponse, PaginatedData
from app.schemas.employee import (
    BulkImportResult,
    EmployeeCreateRequest,
    EmployeeFilterParams,
    EmployeeResponse,
    EmployeeUpdateRequest,
    OrgChartNode,
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get(
    "/org-chart",
    response_model=APIResponse[list[OrgChartNode]],
    summary="Organization chart",
)
async def get_org_chart(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> APIResponse[list[OrgChartNode]]:
    """Get hierarchical organization chart."""
    result = await employee_service.get_org_chart(current_user)
    return APIResponse(success=True, message="Org chart retrieved successfully", data=result)


@router.get(
    "/export",
    summary="Export employees as CSV",
    response_class=PlainTextResponse,
)
async def export_employees(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> PlainTextResponse:
    """Export all active employees as CSV."""
    csv_content = await employee_service.export_csv(current_user)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"},
    )


@router.post(
    "/import",
    response_model=APIResponse[BulkImportResult],
    summary="Import employees from CSV",
)
async def import_employees(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    file: UploadFile = File(...),
) -> APIResponse[BulkImportResult]:
    """Bulk import employees from a CSV file."""
    content = (await file.read()).decode("utf-8")
    result = await employee_service.import_csv(content, current_user)
    return APIResponse(success=True, message="Import completed", data=result)


@router.get(
    "",
    response_model=APIResponse[PaginatedData[EmployeeResponse]],
    summary="List employees",
    description="Retrieve paginated employee list with search, filtering, and sorting. "
    "Results are cached in Redis for 5 minutes.",
)
async def list_employees(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    sort: Annotated[str, Query(pattern=r"^(name|email|department|salary|created_at)$")] = "created_at",
) -> APIResponse[PaginatedData[EmployeeResponse]]:
    """List employees with pagination, search, and filters."""
    filters = EmployeeFilterParams(
        page=page, limit=limit, search=search, department=department, sort=sort
    )
    result = await employee_service.list_employees(filters, current_user)
    return APIResponse(success=True, message="Employees retrieved successfully", data=result)


@router.get(
    "/{employee_id}",
    response_model=APIResponse[EmployeeResponse],
    summary="Get employee by ID",
    description="Retrieve a single employee. EMPLOYEE role can only view their own profile.",
)
async def get_employee(
    employee_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> APIResponse[EmployeeResponse]:
    """Get employee details by ID."""
    result = await employee_service.get_employee(employee_id, current_user)
    return APIResponse(success=True, message="Employee retrieved successfully", data=result)


@router.post(
    "",
    response_model=APIResponse[EmployeeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create employee",
    description="Create a new employee record. Requires ADMIN or MANAGER role.",
)
async def create_employee(
    data: EmployeeCreateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> APIResponse[EmployeeResponse]:
    """Create a new employee."""
    result = await employee_service.create_employee(data, current_user)
    return APIResponse(
        success=True, message="Employee created successfully", data=result
    )


@router.put(
    "/{employee_id}",
    response_model=APIResponse[EmployeeResponse],
    summary="Update employee",
    description="Update an existing employee record. Requires ADMIN or MANAGER role.",
)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> APIResponse[EmployeeResponse]:
    """Update an employee record."""
    result = await employee_service.update_employee(employee_id, data, current_user)
    return APIResponse(
        success=True, message="Employee updated successfully", data=result
    )


@router.delete(
    "/{employee_id}",
    response_model=APIResponse[EmployeeResponse],
    summary="Delete employee",
    description="Soft delete an employee record. Requires ADMIN role.",
)
async def delete_employee(
    employee_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> APIResponse[EmployeeResponse]:
    """Soft delete an employee."""
    result = await employee_service.delete_employee(employee_id, current_user)
    return APIResponse(
        success=True, message="Employee deleted successfully", data=result
    )
