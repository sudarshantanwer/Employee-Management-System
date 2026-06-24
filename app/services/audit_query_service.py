"""Audit log query service."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ForbiddenError
from app.models.enums import Role
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedData
from app.utils.helpers import build_paginated_response


class AuditQueryService:
    """Business logic for querying audit logs."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._audit_repo = AuditLogRepository(db)

    async def list_audit_logs(
        self,
        current_user: UserInDB,
        page: int = 1,
        limit: int = 20,
        action: str | None = None,
        user_id: str | None = None,
    ) -> PaginatedData[AuditLogResponse]:
        """List audit logs. Admin only."""
        if current_user.role != Role.ADMIN:
            raise ForbiddenError("Admin access required")

        documents, total = await self._audit_repo.list_logs(
            page=page, limit=limit, action=action, user_id=user_id
        )
        items = [
            AuditLogResponse(
                id=doc["_id"],
                user_id=doc["user_id"],
                action=doc["action"],
                resource=doc["resource"],
                resource_id=doc.get("resource_id"),
                timestamp=doc["timestamp"],
                metadata=doc.get("metadata", {}),
            )
            for doc in documents
        ]
        return build_paginated_response(items, total, page, limit)
