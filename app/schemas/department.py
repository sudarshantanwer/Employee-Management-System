"""Department request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class DepartmentCreateRequest(BaseModel):
    """Payload for creating a department."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    head_employee_id: str | None = None


class DepartmentUpdateRequest(BaseModel):
    """Payload for updating a department."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    head_employee_id: str | None = None


class DepartmentResponse(BaseModel):
    """Public department representation."""

    id: str
    name: str
    description: str | None
    head_employee_id: str | None
    employee_count: int = 0
    created_at: datetime
    updated_at: datetime
