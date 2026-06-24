"""Department management service."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.department import DepartmentInDB
from app.models.enums import AuditAction, Permission, Role
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from app.services.audit_service import AuditService


class DepartmentService:
    """Business logic for department CRUD operations."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._department_repo = DepartmentRepository(db)
        self._employee_repo = EmployeeRepository(db)
        self._audit_service = AuditService(AuditLogRepository(db))

    async def list_departments(self, current_user: UserInDB) -> list[DepartmentResponse]:
        """List all departments. Available to all authenticated users."""
        documents = await self._department_repo.list_all()
        return [await self._to_response(DepartmentInDB.from_mongo(doc)) for doc in documents]

    async def get_department(
        self, department_id: str, current_user: UserInDB
    ) -> DepartmentResponse:
        """Get a single department by ID."""
        doc = await self._department_repo.get_by_id(department_id)
        if not doc:
            raise NotFoundError("Department not found")
        return await self._to_response(DepartmentInDB.from_mongo(doc))

    async def create_department(
        self, data: DepartmentCreateRequest, current_user: UserInDB
    ) -> DepartmentResponse:
        """Create a new department. Admin only."""
        self._require_admin(current_user)
        existing = await self._department_repo.get_by_name(data.name)
        if existing:
            raise ConflictError("Department with this name already exists")

        department_doc = await self._department_repo.create(data.model_dump())
        department = DepartmentInDB.from_mongo(department_doc)

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.CREATE_DEPARTMENT,
            resource="departments",
            resource_id=department.id,
        )

        return await self._to_response(department)

    async def update_department(
        self,
        department_id: str,
        data: DepartmentUpdateRequest,
        current_user: UserInDB,
    ) -> DepartmentResponse:
        """Update a department. Admin only."""
        self._require_admin(current_user)
        doc = await self._department_repo.get_by_id(department_id)
        if not doc:
            raise NotFoundError("Department not found")

        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing = await self._department_repo.get_by_name(update_data["name"])
            if existing and existing["_id"] != department_id:
                raise ConflictError("Department with this name already exists")

        updated_doc = await self._department_repo.update(department_id, update_data)
        if not updated_doc:
            raise NotFoundError("Department not found")

        department = DepartmentInDB.from_mongo(updated_doc)
        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.UPDATE_DEPARTMENT,
            resource="departments",
            resource_id=department.id,
            metadata=update_data,
        )
        return await self._to_response(department)

    async def delete_department(
        self, department_id: str, current_user: UserInDB
    ) -> DepartmentResponse:
        """Soft delete a department. Admin only."""
        self._require_admin(current_user)
        doc = await self._department_repo.get_by_id(department_id)
        if not doc:
            raise NotFoundError("Department not found")

        deleted_doc = await self._department_repo.soft_delete(department_id)
        if not deleted_doc:
            raise NotFoundError("Department not found")

        department = DepartmentInDB.from_mongo(deleted_doc)
        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.DELETE_DEPARTMENT,
            resource="departments",
            resource_id=department.id,
        )
        return await self._to_response(department)

    async def _to_response(self, department: DepartmentInDB) -> DepartmentResponse:
        count = await self._employee_repo._collection.count_documents(  # noqa: SLF001
            {"is_deleted": False, "department": department.name}
        )
        return DepartmentResponse(
            id=department.id,
            name=department.name,
            description=department.description,
            head_employee_id=department.head_employee_id,
            employee_count=count,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )

    @staticmethod
    def _require_admin(user: UserInDB) -> None:
        if user.role != Role.ADMIN:
            raise ForbiddenError("Admin access required")
