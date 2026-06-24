"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    audit_logs,
    auth,
    departments,
    employees,
    profile,
    users,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router)
api_v1_router.include_router(employees.router)
api_v1_router.include_router(departments.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(profile.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(audit_logs.router)
