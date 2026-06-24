"""Dashboard analytics service."""

import json

import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.enums import Permission
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.analytics import DashboardAnalytics, DepartmentCount, RecentActivity
from app.core.exceptions import ForbiddenError
from app.utils.helpers import cache_key


class AnalyticsService:
    """Business logic for dashboard analytics."""

    CACHE_PREFIX = "analytics:dashboard"
    CACHE_TTL = 120

    def __init__(self, db: AsyncIOMotorDatabase, redis_client: aioredis.Redis) -> None:
        self._employee_repo = EmployeeRepository(db)
        self._department_repo = DepartmentRepository(db)
        self._audit_repo = AuditLogRepository(db)
        self._redis = redis_client

    async def get_dashboard_analytics(
        self, current_user: UserInDB
    ) -> DashboardAnalytics:
        """Get aggregated dashboard metrics. Admin and Manager only."""
        from app.models.enums import ROLE_PERMISSIONS

        permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        if Permission.VIEW_EMPLOYEES not in permissions:
            raise ForbiddenError("Insufficient permissions to view analytics")

        cache_k = cache_key(self.CACHE_PREFIX)
        cached = await self._redis.get(cache_k)
        if cached:
            return DashboardAnalytics.model_validate_json(cached)

        total_employees = await self._employee_repo.count_active()
        total_departments = await self._department_repo.count_active()
        average_salary = await self._employee_repo.average_salary()
        new_hires = await self._employee_repo.count_new_hires_this_month()

        dept_counts_raw = await self._employee_repo.count_by_department()
        employees_by_department = [
            DepartmentCount(department=item["_id"], count=item["count"])
            for item in dept_counts_raw
        ]

        recent_logs = await self._audit_repo.get_recent(limit=10)
        recent_activity = [
            RecentActivity(
                action=log["action"],
                user_id=log["user_id"],
                resource=log["resource"],
                resource_id=log.get("resource_id"),
                timestamp=log["timestamp"],
            )
            for log in recent_logs
        ]

        result = DashboardAnalytics(
            total_employees=total_employees,
            total_departments=total_departments,
            average_salary=average_salary,
            new_hires_this_month=new_hires,
            employees_by_department=employees_by_department,
            recent_activity=recent_activity,
        )

        await self._redis.setex(cache_k, self.CACHE_TTL, result.model_dump_json())
        return result
