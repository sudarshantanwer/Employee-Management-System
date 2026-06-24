"""Authentication service."""

from typing import Any

import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.auth_provider import AuthProvider
from app.models.enums import AuditAction, Role
from app.models.user import UserInDB
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    GoogleAuthRequest,
    GoogleCodeAuthRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.audit_service import AuditService
from app.services.google_auth_service import exchange_google_auth_code, verify_google_id_token
from app.services.token_blacklist_service import TokenBlacklistService
from app.tasks.email_tasks import send_welcome_email


class AuthService:
    """Business logic for authentication and token management."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        redis_client: aioredis.Redis,
    ) -> None:
        self._user_repo = UserRepository(db)
        self._audit_service = AuditService(AuditLogRepository(db))
        self._token_blacklist = TokenBlacklistService(redis_client)

    async def register(self, data: UserRegisterRequest) -> AuthResponse:
        """Register a new user account."""
        existing = await self._user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")

        # Only allow EMPLOYEE role on self-registration unless admin creates users
        if data.role != Role.EMPLOYEE:
            raise ValidationError("Self-registration only supports EMPLOYEE role")

        user_doc = await self._user_repo.create(
            {
                "email": data.email.lower(),
                "hashed_password": hash_password(data.password),
                "full_name": data.full_name,
                "role": data.role.value,
                "auth_provider": AuthProvider.LOCAL.value,
            }
        )
        user = UserInDB.from_mongo(user_doc)

        tokens = self._generate_tokens(user.id, user.role.value)
        send_welcome_email.delay(user.email, user.full_name)

        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            auth_provider=user.auth_provider,
            tokens=tokens,
        )

    async def login(self, data: UserLoginRequest) -> AuthResponse:
        """Authenticate user credentials and return tokens."""
        user_doc = await self._user_repo.get_by_email(data.email)
        if not user_doc:
            raise UnauthorizedError("Invalid email or password")

        user = UserInDB.from_mongo(user_doc)
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        if not user.hashed_password:
            raise UnauthorizedError(
                "This account uses Google sign-in. Please sign in with Google."
            )

        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        tokens = self._generate_tokens(user.id, user.role.value)

        await self._audit_service.log(
            user_id=user.id,
            action=AuditAction.LOGIN,
            resource="auth",
        )

        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            auth_provider=user.auth_provider,
            tokens=tokens,
        )

    async def google_login(self, data: GoogleAuthRequest) -> AuthResponse:
        """Authenticate via Google ID token and return JWT tokens."""
        payload = verify_google_id_token(data.id_token)
        return await self._authenticate_google_payload(payload)

    async def google_login_with_code(self, data: GoogleCodeAuthRequest) -> AuthResponse:
        """Authenticate via Google OAuth authorization code (supports account picker)."""
        payload = await exchange_google_auth_code(data.code)
        return await self._authenticate_google_payload(payload)

    async def _authenticate_google_payload(self, payload: dict[str, Any]) -> AuthResponse:
        """Create or link user from verified Google token payload."""
        google_id = payload["sub"]
        email = payload["email"].lower()
        full_name = payload.get("name") or email.split("@")[0]

        user_doc = await self._user_repo.get_by_google_id(google_id)
        is_new_user = False

        if not user_doc:
            existing = await self._user_repo.get_by_email(email)
            if existing:
                existing_user = UserInDB.from_mongo(existing)
                if existing_user.google_id and existing_user.google_id != google_id:
                    raise ConflictError("Email already linked to a different Google account")
                user_doc = await self._user_repo.update(
                    existing_user.id,
                    {
                        "google_id": google_id,
                        "auth_provider": AuthProvider.GOOGLE.value,
                        "full_name": full_name,
                    },
                )
            else:
                user_doc = await self._user_repo.create(
                    {
                        "email": email,
                        "full_name": full_name,
                        "role": Role.EMPLOYEE.value,
                        "auth_provider": AuthProvider.GOOGLE.value,
                        "google_id": google_id,
                    }
                )
                is_new_user = True

        user = UserInDB.from_mongo(user_doc)  # type: ignore[arg-type]
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        tokens = self._generate_tokens(user.id, user.role.value)

        await self._audit_service.log(
            user_id=user.id,
            action=AuditAction.GOOGLE_LOGIN,
            resource="auth",
            metadata={"is_new_user": is_new_user},
        )

        if is_new_user:
            send_welcome_email.delay(user.email, user.full_name)

        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            auth_provider=user.auth_provider,
            tokens=tokens,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue new token pair using a valid refresh token."""
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        jti = payload.get("jti")
        if jti and await self._token_blacklist.is_blacklisted(jti):
            raise UnauthorizedError("Token has been revoked")

        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
            raise UnauthorizedError("Invalid refresh token")

        user_doc = await self._user_repo.get_by_id(user_id)
        if not user_doc:
            raise UnauthorizedError("User not found")

        user = UserInDB.from_mongo(user_doc)
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        return self._generate_tokens(user.id, user.role.value)

    async def logout(self, access_token: str, refresh_token: str, user_id: str) -> None:
        """Blacklist tokens on logout."""
        settings = get_settings()
        await self._token_blacklist.blacklist_token(
            access_token, settings.jwt_secret_key
        )
        await self._token_blacklist.blacklist_token(
            refresh_token, settings.jwt_refresh_secret_key
        )

        await self._audit_service.log(
            user_id=user_id,
            action=AuditAction.LOGOUT,
            resource="auth",
        )

    def _generate_tokens(self, user_id: str, role: str) -> TokenResponse:
        """Create access and refresh token pair."""
        return TokenResponse(
            access_token=create_access_token(user_id, role),
            refresh_token=create_refresh_token(user_id, role),
        )

    async def get_user_by_id(self, user_id: str) -> UserInDB | None:
        """Retrieve user by ID."""
        user_doc = await self._user_repo.get_by_id(user_id)
        if not user_doc:
            return None
        return UserInDB.from_mongo(user_doc)
