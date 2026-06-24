"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.models.auth_provider import AuthProvider
from app.models.enums import Role


class UserRegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: Role = Role.EMPLOYEE


class UserLoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token payload."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout payload with tokens to blacklist."""

    access_token: str
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Google Sign-In ID token payload from the frontend."""

    id_token: str = Field(min_length=10)


class GoogleCodeAuthRequest(BaseModel):
    """Google OAuth authorization code from the frontend popup flow."""

    code: str = Field(min_length=10)


class AuthResponse(BaseModel):
    """Authentication response with user info and tokens."""

    user_id: str
    email: str
    full_name: str
    role: Role
    auth_provider: AuthProvider = AuthProvider.LOCAL
    tokens: TokenResponse
