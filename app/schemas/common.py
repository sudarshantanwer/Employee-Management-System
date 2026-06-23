"""Common API response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool = True
    message: str = "Operation successful"
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """Paginated list wrapper."""

    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class ErrorDetail(BaseModel):
    """Error detail for failed responses."""

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    message: str
    data: dict[str, Any] | None = None
    errors: list[ErrorDetail] | None = None


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class HealthStatus(BaseModel):
    """Health check component status."""

    status: str
    healthy: bool
    detail: str | None = None


class HealthResponse(BaseModel):
    """Aggregated health check response."""

    application: HealthStatus
    mongodb: HealthStatus
    redis: HealthStatus
