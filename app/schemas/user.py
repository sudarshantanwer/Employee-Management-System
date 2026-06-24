"""User management request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.auth_provider import AuthProvider
from app.models.enums import Role


class UserResponse(BaseModel):
    """Public user representation."""

    id: str
    email: EmailStr
    full_name: str
    role: Role
    auth_provider: AuthProvider
    employee_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    """Admin payload for updating a user."""

    role: Role | None = None
    employee_id: str | None = None
    is_active: bool | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
