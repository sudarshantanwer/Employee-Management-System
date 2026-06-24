"""User management service."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.auth_provider import AuthProvider
from app.models.enums import AuditAction, Role
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedData
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.audit_service import AuditService
from app.utils.helpers import build_paginated_response


class UserService:
    """Business logic for admin user management."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._user_repo = UserRepository(db)
        self._employee_repo = EmployeeRepository(db)
        self._audit_service = AuditService(AuditLogRepository(db))

    async def list_users(
        self,
        current_user: UserInDB,
        page: int = 1,
        limit: int = 10,
        search: str | None = None,
        role: str | None = None,
    ) -> PaginatedData[UserResponse]:
        """List users. Admin only."""
        self._require_admin(current_user)
        documents, total = await self._user_repo.list_users(
            page=page, limit=limit, search=search, role=role
        )
        items = [self._to_response(UserInDB.from_mongo(doc)) for doc in documents]
        return build_paginated_response(items, total, page, limit)

    async def get_user(self, user_id: str, current_user: UserInDB) -> UserResponse:
        """Get user by ID. Admin only."""
        self._require_admin(current_user)
        doc = await self._user_repo.get_by_id(user_id)
        if not doc:
            raise NotFoundError("User not found")
        return self._to_response(UserInDB.from_mongo(doc))

    async def update_user(
        self,
        user_id: str,
        data: UserUpdateRequest,
        current_user: UserInDB,
    ) -> UserResponse:
        """Update user role, employee link, or active status. Admin only."""
        self._require_admin(current_user)
        if user_id == current_user.id and data.is_active is False:
            raise ValidationError("Cannot deactivate your own account")

        doc = await self._user_repo.get_by_id(user_id)
        if not doc:
            raise NotFoundError("User not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(UserInDB.from_mongo(doc))

        if "role" in update_data:
            update_data["role"] = update_data["role"].value

        if "employee_id" in update_data and update_data["employee_id"]:
            employee = await self._employee_repo.get_by_id(update_data["employee_id"])
            if not employee:
                raise NotFoundError("Employee not found for linking")

        updated_doc = await self._user_repo.update(user_id, update_data)
        if not updated_doc:
            raise NotFoundError("User not found")

        user = UserInDB.from_mongo(updated_doc)
        action = (
            AuditAction.DEACTIVATE_USER
            if data.is_active is False
            else AuditAction.UPDATE_USER
        )
        if data.role is not None:
            action = AuditAction.ROLE_CHANGE

        await self._audit_service.log(
            user_id=current_user.id,
            action=action,
            resource="users",
            resource_id=user.id,
            metadata=update_data,
        )
        return self._to_response(user)

    @staticmethod
    def _to_response(user: UserInDB) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            auth_provider=user.auth_provider,
            employee_id=user.employee_id,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def _require_admin(user: UserInDB) -> None:
        if user.role != Role.ADMIN:
            raise ForbiddenError("Admin access required")
