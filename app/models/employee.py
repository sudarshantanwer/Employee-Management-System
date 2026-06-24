"""Employee domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmployeeInDB(BaseModel):
    """Employee document stored in MongoDB."""

    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    department: str
    designation: str
    salary: float
    manager_id: str | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    model_config = {"populate_by_name": True}

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "EmployeeInDB":
        """Create EmployeeInDB from a MongoDB document."""
        doc = dict(document)
        doc["_id"] = str(doc["_id"])
        return cls.model_validate(doc)
