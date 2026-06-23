"""Audit log domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import AuditAction


class AuditLogInDB(BaseModel):
    """Audit log document stored in MongoDB."""

    id: str = Field(alias="_id")
    user_id: str
    action: AuditAction
    resource: str
    resource_id: str | None = None
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "AuditLogInDB":
        """Create AuditLogInDB from a MongoDB document."""
        doc = dict(document)
        doc["_id"] = str(doc["_id"])
        return cls.model_validate(doc)
