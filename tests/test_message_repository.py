import asyncio

import pytest
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from src.database.repository import MessageRepository
from src.database.orm import Message as Message_database
from src.models.messages import Message


@pytest.mark.asyncio(loop_scope='session')
async def test_message_repository_add_success(
        db_client,
    ) -> None:
    session_maker = await db_client()
    message_database = MessageRepository(session_maker)
    data = {
        'sender': 'user1@mail.com',
        'recipient': 'user2@mail.com',
        'content': 'text of message',
        }
    await message_database.add(Message(**data))

    async with session_maker() as session:
        async with session.begin():
            res = await session.execute(text(
                '''
                SELECT sender, recipient, content FROM messages
                '''
            ))
    assert res.first() == tuple(v for v in data.values())

@pytest.mark.asyncio(loop_scope='session')
async def test_message_repository_get_filtered(
        db_client, add_message,
    ) -> None:
    filters = {
        'interlocutor1': 'first_user@mail.com',
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

    session_maker = await db_client()
    message_database = MessageRepository(session_maker)

    res = await message_database.get_dialog(**filters)
    assert len(res) == 2
    fields = ['sender', 'recipient', 'content']
    assert [{f: getattr(r, f) for f in fields} for r in res] == [data1, data2]
