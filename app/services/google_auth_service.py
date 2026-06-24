"""Google ID token verification and OAuth code exchange."""

from typing import Any
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests
from google.oauth2 import id_token
from loguru import logger

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError, ValidationError


def _validate_google_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate required claims on a Google token payload."""
    issuer = payload.get("iss")
    if issuer not in ("accounts.google.com", "https://accounts.google.com"):
        raise UnauthorizedError("Invalid Google token issuer")

    if not payload.get("email_verified", False):
        raise UnauthorizedError("Google email is not verified")

    email = payload.get("email")
    google_id = payload.get("sub")
    if not email or not google_id:
        raise UnauthorizedError("Google token missing required claims")

    return payload


def build_google_authorization_url(prompt: str = "select_account") -> str:
    """Build Google OAuth authorization URL for server-side redirect flow."""
    settings = get_settings()
    if not settings.google_auth_enabled:
        raise ValidationError("Google authentication is not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "prompt": prompt,
        "access_type": "online",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def verify_google_id_token(token: str) -> dict[str, Any]:
    """Verify a Google ID token and return the decoded payload."""
    settings = get_settings()
    if not settings.google_auth_enabled:
        raise ValidationError("Google authentication is not configured")

    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id,
        )
    except ValueError as exc:
        logger.warning("Google token verification failed: {}", exc)
        raise UnauthorizedError("Invalid Google token") from exc

    return _validate_google_payload(payload)


async def exchange_google_auth_code(
    code: str,
    redirect_uri: str | None = None,
) -> dict[str, Any]:
    """Exchange an OAuth authorization code for tokens and return the ID token payload."""
    settings = get_settings()
    if not settings.google_auth_enabled:
        raise ValidationError("Google authentication is not configured")
    if not settings.google_client_secret:
        raise ValidationError(
            "Google Client Secret is not configured. Add GOOGLE_CLIENT_SECRET to .env"
        )

    uri = redirect_uri or settings.google_redirect_uri

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": uri,
                "grant_type": "authorization_code",
            },
        )

    if response.status_code != 200:
        logger.warning("Google code exchange failed: {}", response.text)
        raise UnauthorizedError("Failed to authenticate with Google")

    token_data = response.json()
    id_token_jwt = token_data.get("id_token")
    if not id_token_jwt:
        raise UnauthorizedError("Google did not return an ID token")

    try:
        payload = id_token.verify_oauth2_token(
            id_token_jwt,
            requests.Request(),
            settings.google_client_id,
        )
    except ValueError as exc:
        raise UnauthorizedError("Invalid Google token") from exc

    return _validate_google_payload(payload)
