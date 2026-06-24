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


@pytest.fixture
def mock_google_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Google ID token verification for tests."""

    def fake_verify(token: str) -> dict:
        if token == "invalid-token":
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("Invalid Google token")
        return {
            "sub": "google-user-123",
            "email": "googleuser@test.com",
            "name": "Google User",
            "email_verified": True,
            "iss": "accounts.google.com",
        }

    monkeypatch.setattr(
        "app.services.auth_service.verify_google_id_token",
        fake_verify,
    )


@pytest.mark.asyncio
async def test_google_login_creates_user(client: AsyncClient, mock_google_token: None) -> None:
    """Test Google sign-in creates a new user and returns tokens."""
    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "valid-google-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "googleuser@test.com"
    assert data["data"]["auth_provider"] == "google"
    assert "access_token" in data["data"]["tokens"]


@pytest.mark.asyncio
async def test_google_login_invalid_token(client: AsyncClient, mock_google_token: None) -> None:
    """Test Google sign-in rejects invalid tokens."""
    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_google_login_links_existing_email(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test Google sign-in links to an existing local account by email."""

    def fake_verify_linked(token: str) -> dict:
        return {
            "sub": "google-user-456",
            "email": "existing@test.com",
            "name": "Existing User",
            "email_verified": True,
            "iss": "accounts.google.com",
        }

    monkeypatch.setattr(
        "app.services.auth_service.verify_google_id_token",
        fake_verify_linked,
    )

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@test.com",
            "password": "SecurePass123!",
            "full_name": "Existing User",
            "role": "EMPLOYEE",
        },
    )

    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "valid-link-token"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["auth_provider"] == "google"


@pytest.mark.asyncio
async def test_google_login_with_code(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Google sign-in via authorization code exchange."""

    async def fake_exchange(code: str) -> dict:
        return {
            "sub": "google-code-user",
            "email": "codeuser@test.com",
            "name": "Code User",
            "email_verified": True,
            "iss": "accounts.google.com",
        }

    monkeypatch.setattr(
        "app.services.auth_service.exchange_google_auth_code",
        fake_exchange,
    )

    response = await client.post(
        "/api/v1/auth/google/code",
        json={"code": "valid-auth-code-xyz"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "codeuser@test.com"
