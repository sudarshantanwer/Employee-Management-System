"""Profile request/response schemas."""

from pydantic import BaseModel, EmailStr

from app.models.enums import Role
from app.schemas.employee import EmployeeResponse


class ProfileResponse(BaseModel):
    """Combined user and linked employee profile."""

    user_id: str
    email: EmailStr
    full_name: str
    role: Role
    employee_id: str | None
    employee: EmployeeResponse | None
