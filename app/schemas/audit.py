"""Audit log response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Public audit log representation."""

    id: str
    user_id: str
    action: str
    resource: str
    resource_id: str | None
    timestamp: datetime
    metadata: dict[str, Any] = {}
