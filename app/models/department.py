"""Department domain model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DepartmentInDB(BaseModel):
    """Department document stored in MongoDB."""

    id: str = Field(alias="_id")
    name: str
    description: str | None = None
    head_employee_id: str | None = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    model_config = {"populate_by_name": True}

    @classmethod
    def from_mongo(cls, document: dict[str, Any]) -> "DepartmentInDB":
        """Create DepartmentInDB from a MongoDB document."""
        doc = dict(document)
        doc["_id"] = str(doc["_id"])
        return cls.model_validate(doc)
