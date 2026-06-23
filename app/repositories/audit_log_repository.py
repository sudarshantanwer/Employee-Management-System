"""Audit log repository for MongoDB operations."""

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.enums import AuditAction, CollectionName
from app.repositories.base import serialize_document


class AuditLogRepository:
    """Data access layer for audit_logs collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[CollectionName.AUDIT_LOGS.value]

    async def create_indexes(self) -> None:
        """Ensure required indexes exist."""
        await self._collection.create_index("user_id")
        await self._collection.create_index("action")
        await self._collection.create_index("timestamp")

    async def create(
        self,
        user_id: str,
        action: AuditAction,
        resource: str,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert a new audit log entry."""
        document = {
            "user_id": user_id,
            "action": action.value,
            "resource": resource,
            "resource_id": resource_id,
            "timestamp": datetime.now(UTC),
            "metadata": metadata or {},
        }
        result = await self._collection.insert_one(document)
        created = await self._collection.find_one({"_id": result.inserted_id})
        return serialize_document(created)  # type: ignore[return-value]
