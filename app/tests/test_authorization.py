"""Authorization and RBAC tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthenticated_access_denied(client: AsyncClient) -> None:
    """Test unauthenticated requests are rejected."""
    response = await client.get("/api/v1/employees")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_employee_cannot_list_employees(
    client: AsyncClient, employee_headers: dict[str, str]
) -> None:
    """Test EMPLOYEE role cannot list all employees."""
    response = await client.get("/api/v1/employees", headers=employee_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_manager_can_create_employee(
    client: AsyncClient, manager_headers: dict[str, str]
) -> None:
    """Test MANAGER role can create employees."""
    response = await client.post(
        "/api/v1/employees",
        headers=manager_headers,
        json={
            "name": "John Doe",
            "email": "john@test.com",
            "department": "IT",
            "designation": "Developer",
            "salary": 75000.0,
        },
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_manager_cannot_delete_employee(
    client: AsyncClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    """Test MANAGER role cannot delete employees."""
    create_response = await client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "name": "Jane Doe",
            "email": "jane@test.com",
            "department": "HR",
            "designation": "Manager",
            "salary": 85000.0,
        },
    )
    employee_id = create_response.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/employees/{employee_id}",
        headers=manager_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_delete_employee(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test ADMIN role can delete employees."""
    create_response = await client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "name": "Delete Me",
            "email": "delete@test.com",
            "department": "IT",
            "designation": "Intern",
            "salary": 40000.0,
        },
    )
    employee_id = create_response.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/employees/{employee_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is True


@pytest.mark.asyncio
async def test_employee_can_view_own_profile(
    client: AsyncClient,
    admin_headers: dict[str, str],
    employee_headers: dict[str, str],
    employee_user: dict,
) -> None:
    """Test EMPLOYEE role can view their own linked profile."""
    create_response = await client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "name": "Self View",
            "email": "selfview@test.com",
            "department": "IT",
            "designation": "Engineer",
            "salary": 60000.0,
        },
    )
    employee_id = create_response.json()["data"]["id"]

    # Link employee profile to user
    from app.core.database import db_manager
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_manager.get_database())
    await user_repo.link_employee(employee_user["_id"], employee_id)

    response = await client.get(
        f"/api/v1/employees/{employee_id}",
        headers=employee_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Self View"
