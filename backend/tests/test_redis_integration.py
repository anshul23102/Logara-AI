from unittest.mock import MagicMock, patch

import pytest
import redis

from integrations.redis import RedisQueueClient


@patch("integrations.redis.redis.Redis")
def test_redis_client_connects_lazily(mock_redis):
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    client = RedisQueueClient()

    mock_redis.assert_not_called()
    client.ping()
    mock_redis.assert_called_once()
    mock_client.ping.assert_called_once()


@patch("integrations.redis.redis.Redis")
def test_redis_client_raises_descriptive_error_on_connect_failure(mock_redis):
    mock_redis.side_effect = redis.RedisError("boom")

    client = RedisQueueClient()

    with pytest.raises(RuntimeError, match="Failed to initialize Redis client"):
        client.ping()


@patch("integrations.redis.redis.Redis")
def test_lpush_bounded_pushes_then_trims_to_max_length(mock_redis):
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    client = RedisQueueClient()
    client.lpush_bounded("queue", "payload", max_length=10_000)

    mock_client.lpush.assert_called_once_with("queue", "payload")
    mock_client.ltrim.assert_called_once_with("queue", 0, 9_999)


@patch("integrations.redis.redis.Redis")
def test_lpush_bounded_trims_after_push_not_before(mock_redis):
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    call_order = []
    mock_client.lpush.side_effect = lambda *a: call_order.append("lpush")
    mock_client.ltrim.side_effect = lambda *a: call_order.append("ltrim")

    client = RedisQueueClient()
    client.lpush_bounded("queue", "payload", max_length=5)

    assert call_order == ["lpush", "ltrim"]


@patch("integrations.redis.redis.Redis")
def test_ltrim_delegates_to_underlying_client(mock_redis):
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    client = RedisQueueClient()
    client.ltrim("queue", 0, 99)

    mock_client.ltrim.assert_called_once_with("queue", 0, 99)
