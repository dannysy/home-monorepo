
import pytest
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport

from core.main import app


@pytest.fixture(scope="session")
async def ws_test_client():
    # https://github.com/PacktPublishing/Building-Data-Science-Applications-with-FastAPI-Second-Edition/blob/917a8030e3df10378d26be03465c1560c9f8e3d9/tests/conftest.py#L7
    async with AsyncClient(base_url='http://test', transport=ASGIWebSocketTransport(app)) as client:
        yield {'url': 'http://test/ws', 'client': client}
