"""Department repository for MongoDB operations."""

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.enums import CollectionName
from app.repositories.base import serialize_document, serialize_documents, to_object_id


class DepartmentRepository:
    """Data access layer for departments collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[CollectionName.DEPARTMENTS.value]

    async def create_indexes(self) -> None:
        """Ensure required indexes exist."""
        await self._collection.create_index("name", unique=True)
        await self._collection.create_index("is_deleted")

    async def create(self, department_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new department document."""
        now = datetime.now(UTC)
        department_data.setdefault("created_at", now)
        department_data.setdefault("updated_at", now)
        department_data.setdefault("is_deleted", False)
        result = await self._collection.insert_one(department_data)
        document = await self._collection.find_one({"_id": result.inserted_id})
        return serialize_document(document)  # type: ignore[return-value]

    async def get_by_id(self, department_id: str) -> dict[str, Any] | None:
        """Find department by ID."""
        document = await self._collection.find_one(
            {"_id": to_object_id(department_id), "is_deleted": False}
        )
        return serialize_document(document)

    async def get_by_name(self, name: str) -> dict[str, Any] | None:
        """Find department by name."""
        document = await self._collection.find_one(
            {"name": name, "is_deleted": False}
        )
        return serialize_document(document)

    async def update(
        self, department_id: str, update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update department document."""
        update_data["updated_at"] = datetime.now(UTC)
        result = await self._collection.find_one_and_update(
            {"_id": to_object_id(department_id), "is_deleted": False},
            {"$set": update_data},
            return_document=True,
        )
        return serialize_document(result)

    async def soft_delete(self, department_id: str) -> dict[str, Any] | None:
        """Soft delete a department."""
        return await self.update(department_id, {"is_deleted": True})

    async def list_all(self) -> list[dict[str, Any]]:
        """List all active departments."""
        cursor = self._collection.find({"is_deleted": False}).sort("name", 1)
        documents = await cursor.to_list(length=1000)
        return serialize_documents(documents)

    async def count_active(self) -> int:
        """Count active departments."""
        return await self._collection.count_documents({"is_deleted": False})
