"""Employee profile service for self-service access."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.employee import EmployeeInDB
from app.models.enums import AuditAction, Permission
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.employee import EmployeeProfileUpdateRequest, EmployeeResponse
from app.schemas.profile import ProfileResponse
from app.services.audit_service import AuditService
from app.services.employee_service import EmployeeService


class ProfileService:
    """Business logic for user profile and self-service updates."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._user_repo = UserRepository(db)
        self._employee_repo = EmployeeRepository(db)
        self._audit_service = AuditService(AuditLogRepository(db))

    async def get_profile(self, current_user: UserInDB) -> ProfileResponse:
        """Get current user's profile with linked employee record."""
        employee_response = None
        if current_user.employee_id:
            employee_doc = await self._employee_repo.get_by_id(current_user.employee_id)
            if employee_doc:
                employee_response = EmployeeService._to_response(  # noqa: SLF001
                    EmployeeInDB.from_mongo(employee_doc)
                )

        return ProfileResponse(
            user_id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            employee_id=current_user.employee_id,
            employee=employee_response,
        )

    async def update_profile(
        self,
        data: EmployeeProfileUpdateRequest,
        current_user: UserInDB,
    ) -> ProfileResponse:
        """Update self-service profile fields on linked employee record."""
        if not current_user.employee_id:
            raise NotFoundError(
                "No employee profile linked to your account. Contact an administrator."
            )

        employee_doc = await self._employee_repo.get_by_id(current_user.employee_id)
        if not employee_doc:
            raise NotFoundError("Linked employee profile not found")

        permissions = self._get_user_permissions(current_user)
        if Permission.VIEW_OWN_PROFILE not in permissions:
            raise ForbiddenError("Insufficient permissions")

        if Permission.UPDATE_EMPLOYEE not in permissions:
            # Employees can only update profile fields
            update_data = data.model_dump(exclude_unset=True)
            allowed = {"phone", "address", "emergency_contact"}
            if not update_data.keys() <= allowed:
                raise ForbiddenError("You can only update contact information")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_profile(current_user)

        updated_doc = await self._employee_repo.update(
            current_user.employee_id, update_data
        )
        if not updated_doc:
            raise NotFoundError("Employee profile not found")

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.UPDATE_EMPLOYEE,
            resource="employees",
            resource_id=current_user.employee_id,
            metadata=update_data,
        )

        return await self.get_profile(current_user)

    def _get_user_permissions(self, user: UserInDB) -> set[Permission]:
        from app.models.enums import ROLE_PERMISSIONS

        return ROLE_PERMISSIONS.get(user.role, set())
