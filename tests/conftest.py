import asyncio
import httpx
import pytest
import pytest_asyncio

from src.main import app
from src.models.users import User


@pytest_asyncio.fixture(scope='session')
async def default_client():
    #await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
            transport=transport, base_url='http://app') as client:
        yield client
        # Clean up resources
        #await User.find_all().delete()
