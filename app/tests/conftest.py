"""Pytest configuration and shared fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Configure test environment before importing app modules
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("DATABASE_NAME", "employee_management_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-jwt-access-tokens")
os.environ.setdefault(
    "JWT_REFRESH_SECRET_KEY", "test-secret-key-for-jwt-refresh-tokens"
)
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/14")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/13")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id.apps.googleusercontent.com")

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.database import db_manager
from app.core.redis import redis_manager
from app.core.security import hash_password
from app.main import create_app
from app.models.enums import Role
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository

# Run Celery tasks synchronously in tests
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _ensure_connected() -> None:
    """Connect to MongoDB and Redis for tests."""
    get_settings.cache_clear()
    await db_manager.connect()
    await redis_manager.connect()
    db = db_manager.get_database()
    await UserRepository(db).create_indexes()
    await EmployeeRepository(db).create_indexes()
    await AuditLogRepository(db).create_indexes()
    await DepartmentRepository(db).create_indexes()


async def _clean_database() -> None:
    """Remove all test data from collections and Redis."""
    db = db_manager.get_database()
    await db["users"].delete_many({})
    await db["employees"].delete_many({})
    await db["audit_logs"].delete_many({})
    await db["departments"].delete_many({})
    await redis_manager.get_client().flushdb()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP test client with database connection."""
    await _ensure_connected()
    await _clean_database()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _create_user(
    email: str,
    password: str,
    role: Role,
    full_name: str | None = None,
    employee_id: str | None = None,
) -> dict[str, Any]:
    """Helper to insert a user directly into the database."""
    db = db_manager.get_database()
    user_repo = UserRepository(db)
    user = await user_repo.create(
        {
            "email": email,
            "hashed_password": hash_password(password),
            "full_name": full_name or email.split("@")[0],
            "role": role.value,
            "employee_id": employee_id,
        }
    )
    return user


@pytest_asyncio.fixture
async def admin_user(client: AsyncClient) -> dict[str, Any]:
    """Create an admin user."""
    return await _create_user("admin@test.com", "AdminPass123!", Role.ADMIN)


@pytest_asyncio.fixture
async def manager_user(client: AsyncClient) -> dict[str, Any]:
    """Create a manager user."""
    return await _create_user("manager@test.com", "ManagerPass123!", Role.MANAGER)


@pytest_asyncio.fixture
async def employee_user(client: AsyncClient) -> dict[str, Any]:
    """Create an employee user."""
    return await _create_user("employee@test.com", "EmployeePass123!", Role.EMPLOYEE)


async def login(client: AsyncClient, email: str, password: str) -> dict[str, Any]:
    """Helper to login and return response data."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()


async def auth_headers(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    """Get authorization headers for a user."""
    data = await login(client, email, password)
    token = data["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user: dict[str, Any]) -> dict[str, str]:
    """Authorization headers for admin user."""
    return await auth_headers(client, "admin@test.com", "AdminPass123!")


@pytest_asyncio.fixture
async def manager_headers(
    client: AsyncClient, manager_user: dict[str, Any]
) -> dict[str, str]:
    """Authorization headers for manager user."""
    return await auth_headers(client, "manager@test.com", "ManagerPass123!")


@pytest_asyncio.fixture
async def employee_headers(
    client: AsyncClient, employee_user: dict[str, Any]
) -> dict[str, str]:
    """Authorization headers for employee user."""
    return await auth_headers(client, "employee@test.com", "EmployeePass123!")
