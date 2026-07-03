"""Tests for app_factory startup and lifespan."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.anyio
async def test_lifespan_initializes_qdrant_collection():
    """Verify Qdrant collection is initialized during app startup."""
    with patch("app_factory.qdrant_client") as mock_qdrant, \
         patch("app_factory.init_qdrant_collection") as mock_init, \
         patch("app_factory.IngestionService"), \
         patch("app_factory.LogService"), \
         patch("app_factory.OllamaModelManager") as mock_ollama_class:

        mock_ollama_manager = AsyncMock()
        mock_ollama_class.return_value = mock_ollama_manager

        from app_factory import lifespan
        from fastapi import FastAPI

        app = FastAPI()
        lifespan_gen = lifespan(app)
        await lifespan_gen.__aenter__()

        # Verify init_qdrant_collection was called with client and collection name
        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == mock_qdrant
        assert call_args[0][1] == "logs"

        await lifespan_gen.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_lifespan_calls_ollama_bootstrap():
    """Verify Ollama manager bootstrap is called during app startup."""
    with patch("app_factory.qdrant_client"), \
         patch("app_factory.init_qdrant_collection"), \
         patch("app_factory.IngestionService"), \
         patch("app_factory.LogService"), \
         patch("app_factory.OllamaModelManager") as mock_ollama_class:

        mock_ollama_manager = AsyncMock()
        mock_ollama_class.return_value = mock_ollama_manager

        from app_factory import lifespan
        from fastapi import FastAPI

        app = FastAPI()
        lifespan_gen = lifespan(app)
        await lifespan_gen.__aenter__()

        # Verify Ollama bootstrap was called
        mock_ollama_manager.bootstrap.assert_called_once()

        await lifespan_gen.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_lifespan_closes_qdrant_client_on_shutdown():
    """Verify Qdrant client is closed when app shuts down."""
    with patch("app_factory.qdrant_client") as mock_qdrant, \
         patch("app_factory.init_qdrant_collection"), \
         patch("app_factory.IngestionService"), \
         patch("app_factory.LogService"), \
         patch("app_factory.OllamaModelManager") as mock_ollama_class:

        mock_ollama_manager = AsyncMock()
        mock_ollama_class.return_value = mock_ollama_manager

        from app_factory import lifespan
        from fastapi import FastAPI

        app = FastAPI()
        lifespan_gen = lifespan(app)
        await lifespan_gen.__aenter__()

        # Reset the mock to check close is called in __aexit__
        mock_qdrant.reset_mock()
        await lifespan_gen.__aexit__(None, None, None)

        # Verify Qdrant client close was called
        mock_qdrant.close.assert_called_once()
