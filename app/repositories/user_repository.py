"""User repository for MongoDB operations."""

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.enums import CollectionName, Role
from app.repositories.base import serialize_document, to_object_id


class UserRepository:
    """Data access layer for users collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[CollectionName.USERS.value]

    async def create_indexes(self) -> None:
        """Ensure required indexes exist."""
        await self._collection.create_index("email", unique=True)
        await self._collection.create_index("google_id", unique=True, sparse=True)

    async def get_by_google_id(self, google_id: str) -> dict[str, Any] | None:
        """Find user by Google account ID."""
        document = await self._collection.find_one({"google_id": google_id})
        return serialize_document(document)

    async def create(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new user document."""
        now = datetime.now(UTC)
        user_data.setdefault("created_at", now)
        user_data.setdefault("updated_at", now)
        user_data.setdefault("is_active", True)
        result = await self._collection.insert_one(user_data)
        document = await self._collection.find_one({"_id": result.inserted_id})
        return serialize_document(document)  # type: ignore[return-value]

    async def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Find user by ID."""
        document = await self._collection.find_one({"_id": to_object_id(user_id)})
        return serialize_document(document)

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Find user by email address."""
        document = await self._collection.find_one({"email": email.lower()})
        return serialize_document(document)

    async def update(self, user_id: str, update_data: dict[str, Any]) -> dict[str, Any] | None:
        """Update user document."""
        update_data["updated_at"] = datetime.now(UTC)
        result = await self._collection.find_one_and_update(
            {"_id": to_object_id(user_id)},
            {"$set": update_data},
            return_document=True,
        )
        return serialize_document(result)

    async def update_role(self, user_id: str, role: Role) -> dict[str, Any] | None:
        """Update user role."""
        return await self.update(user_id, {"role": role.value})

    async def link_employee(self, user_id: str, employee_id: str) -> dict[str, Any] | None:
        """Link user to an employee profile."""
        return await self.update(user_id, {"employee_id": employee_id})
