"""Audit log API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import get_audit_query_service
from app.models.user import UserInDB
from app.schemas.audit import AuditLogResponse
from app.schemas.common import APIResponse, PaginatedData
from app.services.audit_query_service import AuditQueryService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[AuditLogResponse]],
    summary="List audit logs",
)
async def list_audit_logs(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    audit_service: Annotated[AuditQueryService, Depends(get_audit_query_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    action: Annotated[str | None, Query()] = None,
    user_id: Annotated[str | None, Query()] = None,
) -> APIResponse[PaginatedData[AuditLogResponse]]:
    """List audit logs. Admin only."""
    result = await audit_service.list_audit_logs(
        current_user, page=page, limit=limit, action=action, user_id=user_id
    )
    return APIResponse(success=True, message="Audit logs retrieved successfully", data=result)
