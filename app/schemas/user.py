"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import Role


class UserResponse(BaseModel):
    """Public user representation."""

    id: str
    email: EmailStr
    full_name: str
    role: Role
    employee_id: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
