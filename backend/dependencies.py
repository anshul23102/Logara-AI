"""FastAPI dependency injection helpers for auth and validation."""

from fastapi import Header, HTTPException

from core.settings import get_settings


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Validate API key from X-API-Key header.

    Raises HTTPException with 403 if key is missing or invalid.
    """
    settings = get_settings()

    if not settings.api_key:
        raise HTTPException(
            status_code=500,
            detail="API key not configured on server",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=403,
            detail="Missing required X-API-Key header",
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )

    return x_api_key
