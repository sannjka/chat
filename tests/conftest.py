import asyncio
import httpx
import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession,
)
from sqlalchemy.sql import text

from src.main import app
from src.database.orm import Base, User, init_db, drop_db, get_session
from src.database.repository import UserRepository
from src.config import get_test_db_url
from src.auth.hash_password import HashPassword


DATABASE_URL = get_test_db_url()
engine = create_async_engine(DATABASE_URL)
override_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
hash_password = HashPassword()

async def override_get_session() -> AsyncSession:
    return override_session_maker

@pytest_asyncio.fixture(scope='function')
async def default_client_function():
    app.dependency_overrides[get_session] = override_get_session
    await init_db(engine)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
            transport=transport, base_url='http://app') as client:
        yield client
        # Clean up resources
        await drop_db(engine)
        app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope='function')
async def db_client():
    app.dependency_overrides[get_session] = override_get_session
    await init_db(engine)

    yield override_get_session
    # Clean up resources
    await drop_db(engine)
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope='function')
async def add_user():
    async def _add_user(username, password, **rest):
        hashed_password = hash_password.create_hash(password)
        async with override_session_maker() as session:
            async with session.begin():
                await session.execute(text(
                    '''
                    INSERT INTO users (username, password)
                    VALUES (:username, :password)
                    '''
                ), dict(username=username, password=hashed_password))
                await session.commit()
    yield _add_user

@pytest.fixture(scope='function')
def ws_client():
    with TestClient(app) as client:
        yield client