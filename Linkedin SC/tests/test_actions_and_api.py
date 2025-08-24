import asyncio
import pytest
from utils import ActionLimiter


def test_action_limiter_basic():
    lim = ActionLimiter(max_actions=2, window_sec=10)
    assert lim.allow() is True
    assert lim.allow() is True
    assert lim.allow() is False
    assert lim.remaining() == 0


@pytest.mark.asyncio
async def test_api_import_and_app():
    # Basic import test to ensure the API module loads
    import api_server
    assert hasattr(api_server, 'app')
