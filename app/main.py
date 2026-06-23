"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.health import router as health_router
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import db_manager
from app.core.logging import setup_logging
from app.core.redis import redis_manager
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.prometheus import PrometheusMiddleware, metrics_endpoint
from app.middleware.request_id import RequestIDMiddleware
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle events."""
    setup_logging()
    settings = get_settings()
    logger.info("Starting {} ({})", settings.app_name, settings.app_env)

    await db_manager.connect()
    await redis_manager.connect()

    db = db_manager.get_database()
    await UserRepository(db).create_indexes()
    await EmployeeRepository(db).create_indexes()
    await AuditLogRepository(db).create_indexes()

    logger.info("Application startup complete")
    yield

    await redis_manager.disconnect()
    await db_manager.disconnect()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Application factory for FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Production-ready Employee Management System API with JWT authentication, "
            "RBAC authorization, MongoDB persistence, Redis caching, and Celery background tasks."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware order: outermost first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    register_exception_handlers(app)

    app.include_router(api_v1_router)
    app.include_router(health_router)
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], tags=["Observability"])

    return app


app = create_app()
