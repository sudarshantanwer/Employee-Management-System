"""Authentication provider types."""

from enum import Enum


class AuthProvider(str, Enum):
    """How the user authenticates."""

    LOCAL = "local"
    GOOGLE = "google"
