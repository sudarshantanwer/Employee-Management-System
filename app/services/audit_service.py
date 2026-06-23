"""Audit logging service."""

from typing import Any

from app.models.enums import AuditAction
from app.repositories.audit_log_repository import AuditLogRepository
from app.tasks.email_tasks import process_audit_log


class AuditService:
    """Business logic for audit trail management."""

    def __init__(self, audit_repo: AuditLogRepository) -> None:
        self._audit_repo = audit_repo

    async def log(
        self,
        user_id: str,
        action: AuditAction,
        resource: str,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Persist audit log and dispatch background processing."""
        await self._audit_repo.create(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            metadata=metadata,
        )
        process_audit_log.delay(
            user_id=user_id,
            action=action.value,
            resource=resource,
            resource_id=resource_id or "",
        )
