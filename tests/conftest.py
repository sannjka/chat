import asyncio
import httpx
import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from src.main import app
from src.models.users import User


@pytest_asyncio.fixture(scope='function')
async def default_client_function():
    #await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
            transport=transport, base_url='http://app') as client:
        yield client
        # Clean up resources
        #await User.find_all().delete()

@pytest.fixture(scope='function')
def ws_client():
    with TestClient(app) as client:
        yield client
