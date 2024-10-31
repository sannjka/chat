import asyncio

import pytest
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from src.database.repository import UserRepository
from src.models.users import User


@pytest.mark.asyncio(loop_scope='session')
async def test_repository_add_success(
        db_client,
    ) -> None:
    session_maker = await db_client()
    user_database = UserRepository(session_maker)
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        }
    await user_database.add(User(**data))

    async with session_maker() as session:
        async with session.begin():
            res = await session.execute(text(
                '''
                SELECT username FROM users
                '''
            ))
    assert res.scalar_one_or_none() == data['username']

@pytest.mark.asyncio(loop_scope='session')
async def test_repository_add_fail(
        db_client, add_user,
    ) -> None:
    # preparation for the Integriti Error
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        }
    await add_user(**data)

    # testing to ad not unique value
    session_maker = await db_client()
    user_database = UserRepository(session_maker)
    with pytest.raises(IntegrityError) as e_info:
        await user_database.add(User(**data))

@pytest.mark.asyncio(loop_scope='session')
async def test_repository_get_one_exists(
        db_client, add_user,
    ) -> None:
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        }
    await add_user(**data)

    session_maker = await db_client()
    user_database = UserRepository(session_maker)

    res = await user_database.get(username=data['username'])
    assert res.username == data['username']

@pytest.mark.asyncio(loop_scope='session')
async def test_repository_get_one_does_not_exist(
        db_client, 
    ) -> None:
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        }

    session_maker = await db_client()
    user_database = UserRepository(session_maker)

    res = await user_database.get(username=data['username'])
    assert res is None

@pytest.mark.asyncio(loop_scope='session')
async def test_repository_get_all(
        db_client, add_user,
    ) -> None:
    data1 = {
        'username': 'first_user@mail.com',
        'password': 'first_password',
        }
    data2 = {
        'username': 'second_user@mail.com',
        'password': 'second_password',
        }
    await asyncio.gather(*[add_user(**data) for data in [data1, data2]])

    session_maker = await db_client()
    user_database = UserRepository(session_maker)

    res = await user_database.list()
    assert len(res) == 2

@pytest.mark.asyncio(loop_scope='session')
async def test_repository_get_filtered(
        db_client, add_user,
    ) -> None:
    data1 = {
        'username': 'first_user@mail.com',
        'password': 'first_password',
        }
    data2 = {
        'username': 'second_user@mail.com',
        'password': 'second_password',
        }
    await asyncio.gather(*[add_user(**data) for data in [data1, data2]])

    session_maker = await db_client()
    user_database = UserRepository(session_maker)

    res = await user_database.list(username=data2['username'])
    assert len(res) == 1
    assert res[0].username == data2['username']
