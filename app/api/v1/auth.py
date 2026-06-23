"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_auth_service, get_current_user
from app.models.user import UserInDB
from app.schemas.auth import (
    AuthResponse,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with EMPLOYEE role. Passwords are hashed with bcrypt.",
)
async def register(
    data: UserRegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[AuthResponse]:
    """Register a new user account."""
    result = await auth_service.register(data)
    return APIResponse(success=True, message="Registration successful", data=result)


@router.post(
    "/login",
    response_model=APIResponse[AuthResponse],
    summary="User login",
    description="Authenticate with email and password. Returns JWT access and refresh tokens.",
)
async def login(
    data: UserLoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[AuthResponse]:
    """Authenticate user and return tokens."""
    result = await auth_service.login(data)
    return APIResponse(success=True, message="Login successful", data=result)


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access and refresh token pair.",
)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[TokenResponse]:
    """Refresh JWT tokens."""
    result = await auth_service.refresh(data.refresh_token)
    return APIResponse(success=True, message="Token refreshed successfully", data=result)


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="User logout",
    description="Blacklist access and refresh tokens in Redis to invalidate the session.",
)
async def logout(
    data: LogoutRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """Logout user and blacklist tokens."""
    await auth_service.logout(
        access_token=data.access_token,
        refresh_token=data.refresh_token,
        user_id=current_user.id,
    )
    return APIResponse(success=True, message="Logout successful", data=None)
