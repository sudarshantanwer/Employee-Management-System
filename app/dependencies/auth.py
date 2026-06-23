"""Authentication dependencies for FastAPI."""

from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.exceptions import UnauthorizedError
from app.core.redis import get_redis
from app.core.security import decode_access_token
from app.models.user import UserInDB
from app.services.auth_service import AuthService
from app.services.token_blacklist_service import TokenBlacklistService

security_scheme = HTTPBearer(auto_error=False)


async def get_auth_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    redis_client: Annotated[aioredis.Redis, Depends(get_redis)],
) -> AuthService:
    """Provide AuthService instance via dependency injection."""
    return AuthService(db, redis_client)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    redis_client: Annotated[aioredis.Redis, Depends(get_redis)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserInDB:
    """Extract and validate the current authenticated user from JWT."""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Authentication credentials not provided")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    jti = payload.get("jti")
    if jti:
        blacklist = TokenBlacklistService(redis_client)
        if await blacklist.is_blacklisted(jti):
            raise UnauthorizedError("Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    user = await auth_service.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    request.state.user_id = user.id
    return user


async def get_optional_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    redis_client: Annotated[aioredis.Redis, Depends(get_redis)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserInDB | None:
    """Return current user if authenticated, otherwise None."""
    if credentials is None or not credentials.credentials:
        return None
    try:
        return await get_current_user(request, credentials, redis_client, auth_service)
    except UnauthorizedError:
        return None
