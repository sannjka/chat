import asyncio

import httpx
import pytest
import pytest_asyncio

from src.auth.jwt_handler import create_access_token
from src.models.messages import Message


@pytest_asyncio.fixture(scope='session')
async def access_token() -> str:
    return create_access_token('tokenuser@mail.com')

@pytest.mark.asyncio(loop_scope='session')
async def test_add_message(
        access_token: str,
        default_client_function: httpx.AsyncClient,
    ) -> None:
    filters = {
        'interlocutor1': 'first_user@mail.com',
        'interlocutor2': 'second_user@mail.com',
    }
    payload = {
        'sender': filters['interlocutor1'],
        'recipient': filters['interlocutor2'],
        'content': 'message1',
        }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    test_response = {
        'message': 'Message created successfully',
    }

    response = await default_client_function.post('/api/v1/message/',
                                                  json=payload,
                                                  headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_retrieve_dialogue(
        default_client_function: httpx.AsyncClient,
        access_token: str,
        add_message,
    ) -> None:
    filters = {
        'interlocutor1': 'tokenuser@mail.com',
        'interlocutor2': 'second_user@mail.com',
    }
    extraneous = 'third_user@mail.com'
    data1 = {
        'sender': filters['interlocutor1'],
        'recipient': filters['interlocutor2'],
        'content': 'message1',
        }
    data2 = {
        'sender': filters['interlocutor2'],
        'recipient': filters['interlocutor1'],
        'content': 'message2',
        }
    data3 = {
        'sender': extraneous,
        'recipient': filters['interlocutor1'],
        'content': 'message3',
        }
    data4 = {
        'sender': filters['interlocutor1'],
        'recipient': extraneous,
        'content': 'message4',
        }
    data = [data1, data2, data3, data4]
    await asyncio.gather(*[add_message(**d) for d in data])

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    url = f'/api/v1/message/{filters["interlocutor2"]}'
    print(url)
    response = await default_client_function.get(url, headers=headers)
    content = response.json()

    assert response.status_code == 200
    fields = ['sender', 'recipient', 'content']
    res_without_id = [{f: r[f] for f in fields} for r in response.json()]
    assert res_without_id == [data1, data2]
