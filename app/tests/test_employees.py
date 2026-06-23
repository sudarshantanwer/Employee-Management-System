"""Employee CRUD endpoint tests."""

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def sample_employee(
    client: AsyncClient, admin_headers: dict[str, str]
) -> dict:
    """Create a sample employee for tests."""
    response = await client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "name": "Alice Smith",
            "email": "alice@test.com",
            "department": "IT",
            "designation": "Senior Developer",
            "salary": 95000.0,
        },
    )
    return response.json()["data"]


@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test creating an employee."""
    response = await client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "name": "Bob Wilson",
            "email": "bob@test.com",
            "department": "Finance",
            "designation": "Analyst",
            "salary": 70000.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Bob Wilson"
    assert data["data"]["is_deleted"] is False


@pytest.mark.asyncio
async def test_list_employees_pagination(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test listing employees with pagination."""
    for i in range(3):
        await client.post(
            "/api/v1/employees",
            headers=admin_headers,
            json={
                "name": f"Employee {i}",
                "email": f"emp{i}@test.com",
                "department": "IT",
                "designation": "Staff",
                "salary": 50000.0 + i * 1000,
            },
        )

    response = await client.get(
        "/api/v1/employees?page=1&limit=2",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["limit"] == 2


@pytest.mark.asyncio
async def test_search_employees(
    client: AsyncClient, admin_headers: dict[str, str], sample_employee: dict
) -> None:
    """Test searching employees by name."""
    response = await client.get(
        "/api/v1/employees?search=Alice",
        headers=admin_headers,
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert any(item["name"] == "Alice Smith" for item in items)


@pytest.mark.asyncio
async def test_filter_by_department(
    client: AsyncClient, admin_headers: dict[str, str], sample_employee: dict
) -> None:
    """Test filtering employees by department."""
    response = await client.get(
        "/api/v1/employees?department=IT",
        headers=admin_headers,
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert all(item["department"] == "IT" for item in items)


@pytest.mark.asyncio
async def test_get_employee_by_id(
    client: AsyncClient, admin_headers: dict[str, str], sample_employee: dict
) -> None:
    """Test retrieving a single employee."""
    response = await client.get(
        f"/api/v1/employees/{sample_employee['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "alice@test.com"


@pytest.mark.asyncio
async def test_update_employee(
    client: AsyncClient, admin_headers: dict[str, str], sample_employee: dict
) -> None:
    """Test updating an employee."""
    response = await client.put(
        f"/api/v1/employees/{sample_employee['id']}",
        headers=admin_headers,
        json={"salary": 100000.0, "designation": "Lead Developer"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["salary"] == 100000.0
    assert data["designation"] == "Lead Developer"


@pytest.mark.asyncio
async def test_soft_delete_employee(
    client: AsyncClient, admin_headers: dict[str, str], sample_employee: dict
) -> None:
    """Test soft deleting an employee."""
    response = await client.delete(
        f"/api/v1/employees/{sample_employee['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_deleted"] is True

    get_response = await client.get(
        f"/api/v1/employees/{sample_employee['id']}",
        headers=admin_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_employee(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test retrieving a non-existent employee returns 404."""
    response = await client.get(
        "/api/v1/employees/507f1f77bcf86cd799439011",
        headers=admin_headers,
    )
    assert response.status_code == 404
