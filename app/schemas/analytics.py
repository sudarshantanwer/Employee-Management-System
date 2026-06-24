"""Analytics response schemas."""

from datetime import datetime

from pydantic import BaseModel


class DepartmentCount(BaseModel):
    """Employee count per department."""

    department: str
    count: int


class RecentActivity(BaseModel):
    """Recent audit log entry for dashboard."""

    action: str
    user_id: str
    resource: str
    resource_id: str | None
    timestamp: datetime


class DashboardAnalytics(BaseModel):
    """Aggregated dashboard metrics."""

    total_employees: int
    total_departments: int
    average_salary: float
    new_hires_this_month: int
    employees_by_department: list[DepartmentCount]
    recent_activity: list[RecentActivity]
