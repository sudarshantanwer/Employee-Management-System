"""MongoDB connection manager using Motor."""

from typing import Any

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class DatabaseManager:
    """Manages async MongoDB connection lifecycle."""

    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Establish MongoDB connection."""
        if self.client is not None:
            return
        settings = get_settings()
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.database_name]
        await self.client.admin.command("ping")
        logger.info("Connected to MongoDB: {}", settings.database_name)

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Disconnected from MongoDB")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Return the active database instance."""
        if self.db is None:
            raise RuntimeError("Database is not connected")
        return self.db

    async def health_check(self) -> dict[str, Any]:
        """Check MongoDB connectivity."""
        try:
            if self.client is None:
                return {"status": "disconnected", "healthy": False}
            await self.client.admin.command("ping")
            return {"status": "connected", "healthy": True}
        except Exception as exc:
            logger.error("MongoDB health check failed: {}", exc)
            return {"status": "error", "healthy": False, "detail": str(exc)}


db_manager = DatabaseManager()


def get_database() -> AsyncIOMotorDatabase:
    """Dependency helper to retrieve the database."""
    return db_manager.get_database()
