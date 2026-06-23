"""JWT token blacklist service using Redis."""

from datetime import UTC, datetime

import redis.asyncio as aioredis
from jose import jwt

from app.core.config import get_settings


class TokenBlacklistService:
    """Manage blacklisted JWT tokens in Redis."""

    PREFIX = "blacklist:"

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    def _key(self, jti: str) -> str:
        return f"{self.PREFIX}{jti}"

    async def blacklist_token(self, token: str, secret_key: str) -> None:
        """Add a token to the blacklist until its natural expiry."""
        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                return

            ttl = int(exp - datetime.now(UTC).timestamp())
            if ttl > 0:
                await self._redis.setex(self._key(jti), ttl, "1")
        except Exception:
            # Token may already be expired or invalid; no need to blacklist
            pass

    async def is_blacklisted(self, jti: str) -> bool:
        """Check if a token JTI is blacklisted."""
        result = await self._redis.get(self._key(jti))
        return result is not None
