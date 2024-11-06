import pytest
import pytest_asyncio

import httpx
from sqlalchemy.sql import text

from src.webapp.utils import send_post_request
from src.auth.jwt_handler import create_access_token


@pytest_asyncio.fixture(scope='session')
async def access_token() -> str:
    return create_access_token('tokenuser@mail.com')

@pytest.mark.asyncio(loop_scope='session')
async def test_send_post_request(
        access_token,
        httpx_client: httpx.AsyncClient,
        db_client,
    ):
    # make request
    access_token = f'Bearer {access_token}'
    url = f'/api/v1/message/'
    payload = {
        'sender': 'tokenuser@mail.com',
        'recipient': 'friend@mail.com',
        'content': 'text of the message',
        }
    response = await send_post_request(
        url, httpx_client, access_token, payload
    )
    # chek the result
    session_maker = await db_client()
    async with session_maker() as session:
        async with session.begin():
            res = await session.execute(text(
                '''
                SELECT sender, recipient, content FROM messages
                '''
            ))
    assert res.first() == tuple(v for v in payload.values())
