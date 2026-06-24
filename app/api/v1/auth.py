"""Authentication API endpoints."""

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.dependencies.auth import get_auth_service, get_current_user
from app.models.user import UserInDB
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    GoogleAuthRequest,
    GoogleCodeAuthRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.google_auth_service import build_google_authorization_url

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _redirect_to_frontend(auth: AuthResponse | None = None, error: str | None = None) -> RedirectResponse:
    """Redirect browser back to the frontend with tokens or an error."""
    settings = get_settings()
    if error:
        params = urlencode({"error": error})
        return RedirectResponse(f"{settings.frontend_url}/auth/google/callback?{params}")

    if auth is None:
        params = urlencode({"error": "Authentication failed"})
        return RedirectResponse(f"{settings.frontend_url}/auth/google/callback?{params}")

    params = urlencode(
        {
            "access_token": auth.tokens.access_token,
            "refresh_token": auth.tokens.refresh_token,
            "user_id": auth.user_id,
            "email": auth.email,
            "full_name": auth.full_name,
            "role": auth.role.value,
        }
    )
    return RedirectResponse(f"{settings.frontend_url}/auth/google/callback?{params}")


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


@router.get(
    "/google/login",
    summary="Start Google Sign-In (redirect)",
    description=(
        "Redirects the browser to Google OAuth. "
        "Use this instead of the JavaScript popup to avoid 'no registered origin' errors."
    ),
)
async def google_login_redirect(
    prompt: Annotated[str, Query()] = "select_account",
) -> RedirectResponse:
    """Redirect user to Google OAuth consent screen."""
    settings = get_settings()
    if not settings.google_auth_enabled:
        raise ValidationError("Google authentication is not configured")
    url = build_google_authorization_url(prompt=prompt)
    return RedirectResponse(url)


@router.get(
    "/google/callback",
    summary="Google OAuth callback",
    include_in_schema=False,
)
async def google_oauth_callback(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    code: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
) -> RedirectResponse:
    """Handle Google OAuth redirect and send tokens to the frontend."""
    if error:
        return _redirect_to_frontend(error=error)
    if not code:
        return _redirect_to_frontend(error="Google did not return an authorization code")

    try:
        result = await auth_service.google_login_with_code(
            GoogleCodeAuthRequest(code=code)
        )
        return _redirect_to_frontend(auth=result)
    except Exception as exc:
        return _redirect_to_frontend(error=str(exc))


@router.post(
    "/google",
    response_model=APIResponse[AuthResponse],
    summary="Google Sign-In",
    description=(
        "Authenticate with a Google ID token from the frontend Google Sign-In button. "
        "Creates a new EMPLOYEE account or links to an existing account by email."
    ),
)
async def google_login(
    data: GoogleAuthRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[AuthResponse]:
    """Authenticate user via Google OAuth ID token."""
    result = await auth_service.google_login(data)
    message = "Google sign-in successful"
    return APIResponse(success=True, message=message, data=result)


@router.post(
    "/google/code",
    response_model=APIResponse[AuthResponse],
    summary="Google Sign-In (account picker)",
    description=(
        "Authenticate with a Google OAuth authorization code. "
        "Use this flow to let users pick or switch Google accounts."
    ),
)
async def google_login_with_code(
    data: GoogleCodeAuthRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[AuthResponse]:
    """Authenticate user via Google OAuth authorization code."""
    result = await auth_service.google_login_with_code(data)
    return APIResponse(success=True, message="Google sign-in successful", data=result)


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


@router.post(
    "/forgot-password",
    response_model=APIResponse[None],
    summary="Request password reset",
    description="Send a password reset email if the account exists and uses local auth.",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """Request password reset email."""
    await auth_service.forgot_password(data.email)
    return APIResponse(
        success=True,
        message="If an account exists with that email, a reset link has been sent.",
        data=None,
    )


@router.post(
    "/reset-password",
    response_model=APIResponse[None],
    summary="Reset password",
    description="Reset password using a valid token from the reset email.",
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> APIResponse[None]:
    """Reset password with token."""
    await auth_service.reset_password(data.token, data.new_password)
    return APIResponse(success=True, message="Password reset successful", data=None)
