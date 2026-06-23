"""Custom exceptions and error codes."""

from typing import Any


class AppException(Exception):
    """Base application exception with HTTP status mapping."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class UnauthorizedError(AppException):
    """Authentication failure (401)."""

    def __init__(
        self,
        message: str = "Not authenticated",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenError(AppException):
    """Authorization failure (403)."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=403, details=details)


class ConflictError(AppException):
    """Conflict with existing resource (409)."""

    def __init__(
        self,
        message: str = "Resource already exists",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=409, details=details)


class ValidationError(AppException):
    """Business validation error (400)."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class InternalServerError(AppException):
    """Internal server error (500)."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=500, details=details)
