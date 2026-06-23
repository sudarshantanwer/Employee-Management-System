"""FastAPI dependency injection package."""

from app.dependencies.auth import get_auth_service, get_current_user, get_optional_current_user
from app.dependencies.rbac import get_employee_service, require_permission, require_role

__all__ = [
    "get_auth_service",
    "get_current_user",
    "get_optional_current_user",
    "get_employee_service",
    "require_permission",
    "require_role",
]
