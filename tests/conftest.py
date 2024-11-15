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
from src.webapp.users import get_users
from src.webapp.utils import get_httpx_client, get_celery_notify
from src.auth.jwt_handler import create_access_token


DATABASE_URL = get_test_db_url()
engine = create_async_engine(DATABASE_URL)
override_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
hash_password = HashPassword()

async def override_get_session() -> AsyncSession:
    return override_session_maker

async def override_get_users() -> str:
    return []

async def override_get_httpx_client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(
            transport=transport, base_url='http://app')

async def override_get_celery_notify():
    class MockPromise:
        def delay(*args, **kwargs):
            print('celery worker:', 'do nothing')
    return MockPromise()

@pytest_asyncio.fixture(scope='function')
async def default_client_function():
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_users] = override_get_users
    app.dependency_overrides[get_celery_notify] = override_get_celery_notify
    await init_db(engine)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
            transport=transport, base_url='http://app') as client:
        yield client
        # Clean up resources
        await drop_db(engine)
        app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope='function')
async def client_for_get_users():
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_httpx_client] = override_get_httpx_client
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

@pytest_asyncio.fixture(scope='function')
async def add_message():
    async def _add_message(sender, recipient, content, **rest):
        async with override_session_maker() as session:
            async with session.begin():
                await session.execute(text(
                    '''
                    INSERT INTO messages (sender, recipient, content)
                    VALUES (:sender, :recipient, :content)
                    '''
                ), dict(sender=sender, recipient=recipient, content=content))
                await session.commit()
    yield _add_message

@pytest.fixture(scope='function')
async def ws_client():
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_celery_notify] = override_get_celery_notify
    await init_db(engine)
    with TestClient(app) as client:
        yield client
        await drop_db(engine)
        app.dependency_overrides.clear()
