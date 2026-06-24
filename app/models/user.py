"""User domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.auth_provider import AuthProvider
from app.models.enums import Role


class UserInDB(BaseModel):
    """User document stored in MongoDB."""

    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str | None = None
    full_name: str
    role: Role
    auth_provider: AuthProvider = AuthProvider.LOCAL
    google_id: str | None = None
    employee_id: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "UserInDB":
        """Create UserInDB from a MongoDB document."""
        doc = dict(document)
        doc["_id"] = str(doc["_id"])
        return cls.model_validate(doc)
