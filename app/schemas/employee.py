"""Employee request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreateRequest(BaseModel):
    """Payload for creating an employee."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    department: str = Field(min_length=1, max_length=100)
    designation: str = Field(min_length=1, max_length=100)
    salary: float = Field(gt=0)
    manager_id: str | None = None


class EmployeeUpdateRequest(BaseModel):
    """Payload for updating an employee."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    department: str | None = Field(default=None, min_length=1, max_length=100)
    designation: str | None = Field(default=None, min_length=1, max_length=100)
    salary: float | None = Field(default=None, gt=0)
    manager_id: str | None = None


class EmployeeResponse(BaseModel):
    """Public employee representation."""

    id: str
    name: str
    email: EmailStr
    department: str
    designation: str
    salary: float
    manager_id: str | None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False


class EmployeeFilterParams(BaseModel):
    """Query parameters for employee list filtering."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    department: str | None = None
    sort: str = Field(default="created_at", pattern=r"^(name|email|department|salary|created_at)$")
