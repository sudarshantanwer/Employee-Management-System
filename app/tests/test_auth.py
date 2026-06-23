"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "role": "EMPLOYEE",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "newuser@test.com"
    assert "access_token" in data["data"]["tokens"]
    assert "refresh_token" in data["data"]["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Test registration with duplicate email fails."""
    payload = {
        "email": "duplicate@test.com",
        "password": "SecurePass123!",
        "full_name": "Duplicate User",
        "role": "EMPLOYEE",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_register_admin_role_rejected(client: AsyncClient) -> None:
    """Test self-registration with ADMIN role is rejected."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "fakeadmin@test.com",
            "password": "SecurePass123!",
            "full_name": "Fake Admin",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: dict) -> None:
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["role"] == "ADMIN"
    assert data["data"]["tokens"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, admin_user: dict) -> None:
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_user: dict) -> None:
    """Test token refresh."""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    refresh_token = login_response.json()["data"]["tokens"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_logout_blacklists_token(client: AsyncClient, admin_user: dict) -> None:
    """Test logout blacklists tokens."""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    tokens = login_response.json()["data"]["tokens"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        },
    )
    assert logout_response.status_code == 200

    # Access token should be rejected after logout
    protected_response = await client.get(
        "/api/v1/employees",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert protected_response.status_code == 401
