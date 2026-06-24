"""Tests for Tier 1 features."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_departments(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Admin can list departments."""
    await client.post(
        "/api/v1/departments",
        json={"name": "TestDept", "description": "Test"},
        headers=admin_headers,
    )
    response = await client.get("/api/v1/departments", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(d["name"] == "TestDept" for d in data)


@pytest.mark.asyncio
async def test_create_department_requires_admin(
    client: AsyncClient, manager_headers: dict[str, str]
) -> None:
    """Managers cannot create departments."""
    response = await client.post(
        "/api/v1/departments",
        json={"name": "ForbiddenDept"},
        headers=manager_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Admin can list users."""
    response = await client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_admin_update_user_role(
    client: AsyncClient, admin_headers: dict[str, str], employee_user: dict
) -> None:
    """Admin can change user role."""
    response = await client.put(
        f"/api/v1/users/{employee_user['_id']}",
        json={"role": "MANAGER"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["role"] == "MANAGER"


@pytest.mark.asyncio
async def test_profile_me(
    client: AsyncClient,
    admin_headers: dict[str, str],
    employee_headers: dict[str, str],
) -> None:
    """Authenticated user can get profile."""
    response = await client.get("/api/v1/profile/me", headers=employee_headers)
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "employee@test.com"


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient, admin_user: dict) -> None:
    """Forgot password returns success without revealing account existence."""
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "admin@test.com"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient) -> None:
    """Reset password rejects invalid token."""
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid-token", "new_password": "NewPass123!"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_audit_logs_admin_only(
    client: AsyncClient,
    admin_headers: dict[str, str],
    employee_headers: dict[str, str],
) -> None:
    """Only admin can view audit logs."""
    admin_resp = await client.get("/api/v1/audit-logs", headers=admin_headers)
    assert admin_resp.status_code == 200

    emp_resp = await client.get("/api/v1/audit-logs", headers=employee_headers)
    assert emp_resp.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_analytics(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Admin/manager can get dashboard analytics."""
    response = await client.get("/api/v1/analytics/dashboard", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_employees" in data
    assert "employees_by_department" in data


@pytest.mark.asyncio
async def test_org_chart(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Admin can get org chart."""
    create_resp = await client.post(
        "/api/v1/employees",
        json={
            "name": "Manager One",
            "email": "mgr1@test.com",
            "department": "IT",
            "designation": "Manager",
            "salary": 100000,
        },
        headers=admin_headers,
    )
    manager_id = create_resp.json()["data"]["id"]

    await client.post(
        "/api/v1/employees",
        json={
            "name": "Report One",
            "email": "rep1@test.com",
            "department": "IT",
            "designation": "Developer",
            "salary": 80000,
            "manager_id": manager_id,
        },
        headers=admin_headers,
    )

    response = await client.get("/api/v1/employees/org-chart", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_export_import_csv(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Admin can export and import employees via CSV."""
    export_resp = await client.get("/api/v1/employees/export", headers=admin_headers)
    assert export_resp.status_code == 200
    assert "text/csv" in export_resp.headers.get("content-type", "")

    csv_content = (
        "name,email,department,designation,salary\n"
        "CSV User,csvuser@test.com,IT,Developer,75000\n"
    )
    import_resp = await client.post(
        "/api/v1/employees/import",
        files={"file": ("employees.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        headers=admin_headers,
    )
    assert import_resp.status_code == 200
    result = import_resp.json()["data"]
    assert result["created"] == 1
