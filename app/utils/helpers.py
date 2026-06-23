"""Shared utility functions."""

import json
from typing import Any

from app.schemas.common import PaginatedData


def build_paginated_response(
    items: list[Any],
    total: int,
    page: int,
    limit: int,
) -> PaginatedData[Any]:
    """Build a paginated response wrapper."""
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return PaginatedData(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


def cache_key(prefix: str, **params: Any) -> str:
    """Generate a deterministic Redis cache key."""
    sorted_params = sorted(params.items())
    param_str = json.dumps(sorted_params, default=str)
    return f"{prefix}:{param_str}"
