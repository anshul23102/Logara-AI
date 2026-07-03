"""Tests for auth dependencies."""

import pytest
from fastapi import HTTPException
from unittest.mock import patch

from dependencies import verify_api_key


@pytest.mark.anyio
async def test_verify_api_key_missing_header():
    """Verify that missing X-API-Key header raises 403."""
    with patch("dependencies.get_settings") as mock_settings:
        mock_settings.return_value.api_key = "valid-secret-key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key=None)

        assert exc_info.value.status_code == 403
        assert "Missing required X-API-Key header" in exc_info.value.detail


@pytest.mark.anyio
async def test_verify_api_key_invalid():
    """Verify that invalid API key raises 403."""
    with patch("dependencies.get_settings") as mock_settings:
        mock_settings.return_value.api_key = "valid-secret-key"

        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key="wrong-key")

        assert exc_info.value.status_code == 403
        assert "Invalid API key" in exc_info.value.detail


@pytest.mark.anyio
async def test_verify_api_key_valid():
    """Verify that valid API key is accepted."""
    with patch("dependencies.get_settings") as mock_settings:
        mock_settings.return_value.api_key = "valid-secret-key"

        result = await verify_api_key(x_api_key="valid-secret-key")

        assert result == "valid-secret-key"


@pytest.mark.anyio
async def test_verify_api_key_not_configured():
    """Verify that missing server config raises 500."""
    with patch("dependencies.get_settings") as mock_settings:
        mock_settings.return_value.api_key = None

        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(x_api_key="any-key")

        assert exc_info.value.status_code == 500
        assert "not configured" in exc_info.value.detail
