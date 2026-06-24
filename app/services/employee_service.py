"""Employee management service."""

import csv
import io
import json
from typing import Any

import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.employee import EmployeeInDB
from app.models.enums import AuditAction, Permission
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.common import PaginatedData
from app.schemas.employee import (
    BulkImportResult,
    EmployeeCreateRequest,
    EmployeeFilterParams,
    EmployeeResponse,
    EmployeeUpdateRequest,
    OrgChartNode,
)
from app.services.audit_service import AuditService
from app.utils.helpers import build_paginated_response, cache_key


class EmployeeService:
    """Business logic for employee CRUD operations."""

    CACHE_PREFIX = "employees:list"

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        redis_client: aioredis.Redis,
    ) -> None:
        self._employee_repo = EmployeeRepository(db)
        self._audit_service = AuditService(AuditLogRepository(db))
        self._redis = redis_client
        self._settings = get_settings()

    async def list_employees(
        self,
        filters: EmployeeFilterParams,
        current_user: UserInDB,
    ) -> PaginatedData[EmployeeResponse]:
        """List employees with caching, filtering, and pagination."""
        if Permission.VIEW_EMPLOYEES not in self._get_user_permissions(current_user):
            raise ForbiddenError("Insufficient permissions to view employees")

        cache_k = cache_key(
            self.CACHE_PREFIX,
            page=filters.page,
            limit=filters.limit,
            search=filters.search,
            department=filters.department,
            sort=filters.sort,
        )

        cached = await self._redis.get(cache_k)
        if cached:
            data = json.loads(cached)
            data["items"] = [EmployeeResponse(**item) for item in data["items"]]
            return PaginatedData[EmployeeResponse](**data)

        documents, total = await self._employee_repo.list_with_filters(
            page=filters.page,
            limit=filters.limit,
            search=filters.search,
            department=filters.department,
            sort=filters.sort,
        )

        items = [self._to_response(EmployeeInDB.from_mongo(doc)) for doc in documents]
        result = build_paginated_response(items, total, filters.page, filters.limit)

        await self._redis.setex(
            cache_k,
            self._settings.employee_cache_ttl_seconds,
            result.model_dump_json(),
        )

        return result

    async def get_employee(
        self,
        employee_id: str,
        current_user: UserInDB,
    ) -> EmployeeResponse:
        """Get a single employee by ID with authorization."""
        employee_doc = await self._employee_repo.get_by_id(employee_id)
        if not employee_doc:
            raise NotFoundError("Employee not found")

        employee = EmployeeInDB.from_mongo(employee_doc)
        self._authorize_view(employee, current_user)
        return self._to_response(employee)

    async def create_employee(
        self,
        data: EmployeeCreateRequest,
        current_user: UserInDB,
    ) -> EmployeeResponse:
        """Create a new employee record."""
        self._require_permission(current_user, Permission.CREATE_EMPLOYEE)

        existing = await self._employee_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Employee with this email already exists")

        employee_doc = await self._employee_repo.create(data.model_dump())
        employee = EmployeeInDB.from_mongo(employee_doc)

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.CREATE_EMPLOYEE,
            resource="employees",
            resource_id=employee.id,
        )

        await self._invalidate_cache()
        return self._to_response(employee)

    async def update_employee(
        self,
        employee_id: str,
        data: EmployeeUpdateRequest,
        current_user: UserInDB,
    ) -> EmployeeResponse:
        """Update an existing employee record."""
        self._require_permission(current_user, Permission.UPDATE_EMPLOYEE)

        employee_doc = await self._employee_repo.get_by_id(employee_id)
        if not employee_doc:
            raise NotFoundError("Employee not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(EmployeeInDB.from_mongo(employee_doc))

        if "email" in update_data:
            existing = await self._employee_repo.get_by_email(update_data["email"])
            if existing and existing["_id"] != employee_id:
                raise ConflictError("Employee with this email already exists")

        updated_doc = await self._employee_repo.update(employee_id, update_data)
        if not updated_doc:
            raise NotFoundError("Employee not found")

        employee = EmployeeInDB.from_mongo(updated_doc)

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.UPDATE_EMPLOYEE,
            resource="employees",
            resource_id=employee.id,
            metadata=update_data,
        )

        await self._invalidate_cache()
        return self._to_response(employee)

    async def delete_employee(
        self,
        employee_id: str,
        current_user: UserInDB,
    ) -> EmployeeResponse:
        """Soft delete an employee record."""
        self._require_permission(current_user, Permission.DELETE_EMPLOYEE)

        employee_doc = await self._employee_repo.get_by_id(employee_id)
        if not employee_doc:
            raise NotFoundError("Employee not found")

        deleted_doc = await self._employee_repo.soft_delete(employee_id)
        if not deleted_doc:
            raise NotFoundError("Employee not found")

        employee = EmployeeInDB.from_mongo(deleted_doc)

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.DELETE_EMPLOYEE,
            resource="employees",
            resource_id=employee.id,
        )

        await self._invalidate_cache()
        return self._to_response(employee)

    async def get_org_chart(self, current_user: UserInDB) -> list[OrgChartNode]:
        """Build hierarchical org chart from manager relationships."""
        if Permission.VIEW_EMPLOYEES not in self._get_user_permissions(current_user):
            raise ForbiddenError("Insufficient permissions to view org chart")

        documents = await self._employee_repo.list_all_active()
        employees = [EmployeeInDB.from_mongo(doc) for doc in documents]

        nodes: dict[str, OrgChartNode] = {}
        for emp in employees:
            nodes[emp.id] = OrgChartNode(
                id=emp.id,
                name=emp.name,
                designation=emp.designation,
                department=emp.department,
                manager_id=emp.manager_id,
                children=[],
            )

        roots: list[OrgChartNode] = []
        for emp in employees:
            node = nodes[emp.id]
            if emp.manager_id and emp.manager_id in nodes:
                nodes[emp.manager_id].children.append(node)
            else:
                roots.append(node)

        return roots

    async def export_csv(self, current_user: UserInDB) -> str:
        """Export all active employees as CSV string."""
        if Permission.VIEW_EMPLOYEES not in self._get_user_permissions(current_user):
            raise ForbiddenError("Insufficient permissions to export employees")

        documents = await self._employee_repo.list_all_active()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "name",
                "email",
                "department",
                "designation",
                "salary",
                "manager_id",
                "phone",
                "address",
                "emergency_contact",
            ]
        )
        for doc in documents:
            writer.writerow(
                [
                    doc.get("name", ""),
                    doc.get("email", ""),
                    doc.get("department", ""),
                    doc.get("designation", ""),
                    doc.get("salary", ""),
                    doc.get("manager_id") or "",
                    doc.get("phone") or "",
                    doc.get("address") or "",
                    doc.get("emergency_contact") or "",
                ]
            )
        return output.getvalue()

    async def import_csv(
        self, csv_content: str, current_user: UserInDB
    ) -> BulkImportResult:
        """Bulk import employees from CSV content."""
        self._require_permission(current_user, Permission.CREATE_EMPLOYEE)

        reader = csv.DictReader(io.StringIO(csv_content))
        required_fields = {"name", "email", "department", "designation", "salary"}
        if not reader.fieldnames or not required_fields.issubset(
            set(reader.fieldnames)
        ):
            raise ValidationError(
                "CSV must include columns: name, email, department, designation, salary"
            )

        created = 0
        skipped = 0
        errors: list[str] = []
        to_insert: list[dict[str, Any]] = []

        for row_num, row in enumerate(reader, start=2):
            email = (row.get("email") or "").strip().lower()
            if not email:
                errors.append(f"Row {row_num}: missing email")
                skipped += 1
                continue

            existing = await self._employee_repo.get_by_email(email)
            if existing:
                errors.append(f"Row {row_num}: email {email} already exists")
                skipped += 1
                continue

            try:
                salary = float(row.get("salary", 0))
                if salary <= 0:
                    raise ValueError("salary must be positive")
            except (TypeError, ValueError):
                errors.append(f"Row {row_num}: invalid salary")
                skipped += 1
                continue

            employee_data: dict[str, Any] = {
                "name": (row.get("name") or "").strip(),
                "email": email,
                "department": (row.get("department") or "").strip(),
                "designation": (row.get("designation") or "").strip(),
                "salary": salary,
            }
            if not all(
                [
                    employee_data["name"],
                    employee_data["department"],
                    employee_data["designation"],
                ]
            ):
                errors.append(f"Row {row_num}: missing required fields")
                skipped += 1
                continue

            manager_id = (row.get("manager_id") or "").strip()
            if manager_id:
                employee_data["manager_id"] = manager_id
            phone = (row.get("phone") or "").strip()
            if phone:
                employee_data["phone"] = phone
            address = (row.get("address") or "").strip()
            if address:
                employee_data["address"] = address
            emergency = (row.get("emergency_contact") or "").strip()
            if emergency:
                employee_data["emergency_contact"] = emergency

            to_insert.append(employee_data)

        if to_insert:
            created = await self._employee_repo.bulk_create(to_insert)

        await self._audit_service.log(
            user_id=current_user.id,
            action=AuditAction.BULK_IMPORT_EMPLOYEES,
            resource="employees",
            metadata={"created": created, "skipped": skipped},
        )

        await self._invalidate_cache()
        return BulkImportResult(created=created, skipped=skipped, errors=errors)

    async def _invalidate_cache(self) -> None:
        """Remove all employee list cache entries."""
        pattern = f"{self.CACHE_PREFIX}:*"
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)

    def _get_user_permissions(self, user: UserInDB) -> set[Permission]:
        from app.models.enums import ROLE_PERMISSIONS

        return ROLE_PERMISSIONS.get(user.role, set())

    def _require_permission(self, user: UserInDB, permission: Permission) -> None:
        if permission not in self._get_user_permissions(user):
            raise ForbiddenError(f"Missing permission: {permission.value}")

    def _authorize_view(self, employee: EmployeeInDB, user: UserInDB) -> None:
        permissions = self._get_user_permissions(user)
        if Permission.VIEW_EMPLOYEES in permissions:
            return
        if Permission.VIEW_OWN_PROFILE in permissions and user.employee_id == employee.id:
            return
        raise ForbiddenError("Insufficient permissions to view this employee")

    @staticmethod
    def _to_response(employee: EmployeeInDB) -> EmployeeResponse:
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            department=employee.department,
            designation=employee.designation,
            salary=employee.salary,
            manager_id=employee.manager_id,
            phone=employee.phone,
            address=employee.address,
            emergency_contact=employee.emergency_contact,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            is_deleted=employee.is_deleted,
        )
