"""Redis connection manager for caching and token blacklist."""

from typing import Any

import redis.asyncio as aioredis
from loguru import logger

from app.core.config import get_settings


class RedisManager:
    """Manages async Redis connection lifecycle."""

    client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Establish Redis connection."""
        if self.client is not None:
            return
        settings = get_settings()
        self.client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self.client.ping()
        logger.info("Connected to Redis")

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Disconnected from Redis")

    def get_client(self) -> aioredis.Redis:
        """Return the active Redis client."""
        if self.client is None:
            raise RuntimeError("Redis is not connected")
        return self.client

    async def health_check(self) -> dict[str, Any]:
        """Check Redis connectivity."""
        try:
            if self.client is None:
                return {"status": "disconnected", "healthy": False}
            await self.client.ping()
            return {"status": "connected", "healthy": True}
        except Exception as exc:
            logger.error("Redis health check failed: {}", exc)
            return {"status": "error", "healthy": False, "detail": str(exc)}


redis_manager = RedisManager()


def get_redis() -> aioredis.Redis:
    """Dependency helper to retrieve Redis client."""
    return redis_manager.get_client()
