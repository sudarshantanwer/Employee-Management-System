"""Role-Based Access Control dependencies."""

from collections.abc import Callable
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.exceptions import ForbiddenError
from app.core.redis import get_redis
from app.dependencies.auth import get_current_user
from app.models.enums import ROLE_PERMISSIONS, Permission, Role
from app.models.user import UserInDB
from app.services.employee_service import EmployeeService


def require_role(*roles: Role) -> Callable:
    """Dependency factory requiring one of the specified roles."""

    async def role_checker(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
    ) -> UserInDB:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Access denied. Required role(s): {', '.join(r.value for r in roles)}"
            )
        return current_user

    return role_checker


def require_permission(*permissions: Permission) -> Callable:
    """Dependency factory requiring specific permissions."""

    async def permission_checker(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
    ) -> UserInDB:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        for permission in permissions:
            if permission not in user_permissions:
                raise ForbiddenError(
                    f"Missing required permission: {permission.value}"
                )
        return current_user

    return permission_checker


async def get_employee_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    redis_client: Annotated[aioredis.Redis, Depends(get_redis)],
) -> EmployeeService:
    """Provide EmployeeService instance via dependency injection."""
    return EmployeeService(db, redis_client)
