"""Employee repository for MongoDB operations."""

import re
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.enums import CollectionName
from app.repositories.base import serialize_document, serialize_documents, to_object_id


class EmployeeRepository:
    """Data access layer for employees collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[CollectionName.EMPLOYEES.value]

    async def create_indexes(self) -> None:
        """Ensure required indexes exist."""
        await self._collection.create_index("email", unique=True)
        await self._collection.create_index("department")
        await self._collection.create_index("is_deleted")
        await self._collection.create_index("name")

    async def create(self, employee_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new employee document."""
        now = datetime.now(UTC)
        employee_data.setdefault("created_at", now)
        employee_data.setdefault("updated_at", now)
        employee_data.setdefault("is_deleted", False)
        result = await self._collection.insert_one(employee_data)
        document = await self._collection.find_one({"_id": result.inserted_id})
        return serialize_document(document)  # type: ignore[return-value]

    async def get_by_id(
        self, employee_id: str, include_deleted: bool = False
    ) -> dict[str, Any] | None:
        """Find employee by ID."""
        query: dict[str, Any] = {"_id": to_object_id(employee_id)}
        if not include_deleted:
            query["is_deleted"] = False
        document = await self._collection.find_one(query)
        return serialize_document(document)

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Find active employee by email."""
        document = await self._collection.find_one(
            {"email": email.lower(), "is_deleted": False}
        )
        return serialize_document(document)

    async def update(
        self, employee_id: str, update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update employee document."""
        update_data["updated_at"] = datetime.now(UTC)
        result = await self._collection.find_one_and_update(
            {"_id": to_object_id(employee_id), "is_deleted": False},
            {"$set": update_data},
            return_document=True,
        )
        return serialize_document(result)

    async def soft_delete(self, employee_id: str) -> dict[str, Any] | None:
        """Soft delete an employee."""
        return await self.update(employee_id, {"is_deleted": True})

    async def list_with_filters(
        self,
        page: int = 1,
        limit: int = 10,
        search: str | None = None,
        department: str | None = None,
        sort: str = "created_at",
    ) -> tuple[list[dict[str, Any]], int]:
        """List employees with pagination, search, and filtering."""
        query: dict[str, Any] = {"is_deleted": False}

        if department:
            query["department"] = department

        if search:
            regex = re.compile(re.escape(search), re.IGNORECASE)
            query["$or"] = [
                {"name": regex},
                {"email": regex},
                {"department": regex},
                {"designation": regex},
            ]

        sort_direction = 1 if sort == "name" else -1
        sort_field = sort if sort != "name" else "name"

        total = await self._collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = (
            self._collection.find(query)
            .sort(sort_field, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        return serialize_documents(documents), total

    async def list_all_active(self) -> list[dict[str, Any]]:
        """List all active employees for org chart and export."""
        cursor = self._collection.find({"is_deleted": False}).sort("name", 1)
        documents = await cursor.to_list(length=10000)
        return serialize_documents(documents)

    async def count_active(self) -> int:
        """Count active employees."""
        return await self._collection.count_documents({"is_deleted": False})

    async def count_by_department(self) -> list[dict[str, Any]]:
        """Aggregate employee counts by department."""
        pipeline = [
            {"$match": {"is_deleted": False}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        return await self._collection.aggregate(pipeline).to_list(length=100)

    async def average_salary(self) -> float:
        """Calculate average salary of active employees."""
        pipeline = [
            {"$match": {"is_deleted": False}},
            {"$group": {"_id": None, "avg": {"$avg": "$salary"}}},
        ]
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        if result and result[0].get("avg") is not None:
            return round(float(result[0]["avg"]), 2)
        return 0.0

    async def count_new_hires_this_month(self) -> int:
        """Count employees created in the current calendar month."""
        now = datetime.now(UTC)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return await self._collection.count_documents(
            {"is_deleted": False, "created_at": {"$gte": start_of_month}}
        )

    async def bulk_create(self, employees: list[dict[str, Any]]) -> int:
        """Insert multiple employee documents."""
        if not employees:
            return 0
        now = datetime.now(UTC)
        for emp in employees:
            emp.setdefault("created_at", now)
            emp.setdefault("updated_at", now)
            emp.setdefault("is_deleted", False)
        result = await self._collection.insert_many(employees)
        return len(result.inserted_ids)
