from datetime import timedelta

import httpx
import pytest
import pytest_asyncio

from src.auth.jwt_handler import create_access_token


@pytest_asyncio.fixture(scope='session')
async def access_token() -> str:
    return create_access_token('tokenuser@mail.com')

@pytest_asyncio.fixture(scope='session')
async def wrong_token() -> str:
    return create_access_token('wronguser@mail.com')

@pytest_asyncio.fixture(scope='session')
async def expired_token() -> str:
    return create_access_token(
        'testuser@mail.com',
        timedelta(minutes=-1),
    )

@pytest.mark.asyncio(loop_scope='session')
async def test_sign_new_user(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    payload = {
        'username': 'testuser@mail.com',
        'password': 'testpassword!',
    }
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    test_response = {
        'message': 'User successfully registered!',
    }

    response = await default_client_function.post('/api/v1/user/signup',
                                                  json=payload,
                                                  headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_sign_user_in(
        default_client_function: httpx.AsyncClient,
        add_user,
    ) -> None:
    data = {
        'username': 'testuser@mail.com',
        'password': 'testpassword!',
        }
    await add_user(**data)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = await default_client_function.post('/api/v1/user/signin',
                                                  data=data,
                                                  headers=headers)
    assert response.status_code == 200
    assert response.json()['token_type'] == 'Bearer'

@pytest.mark.asyncio(loop_scope='session')
async def test_sign_wrong_user_name_in(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    payload = {
        'username': 'wronguser@mail.com',
        'password': 'testpassword',
    }
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    test_response = {
        'detail': 'User with supplied email does not exist',
    }

    response = await default_client_function.post('/api/v1/user/signin',
                                                  data=payload,
                                                  headers=headers)
    assert response.status_code == 404
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_sign_wrong_password_in(
        default_client_function: httpx.AsyncClient,
        add_user,
    ) -> None:
    data = {
        'username': 'testuser@mail.com',
        'password': 'testpassword!',
        }
    await add_user(**data)
    data['password'] = 'wrongpassword'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    test_response = {
        'detail': 'Invalid details passed.',
    }

    response = await default_client_function.post('/api/v1/user/signin',
                                                  data=data,
                                                  headers=headers)
    assert response.status_code == 401
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_retrieve_all_users(
        default_client_function: httpx.AsyncClient,
        access_token: str,
        add_user,
    ) -> None:
    data = {
        'username': 'tokenuser@mail.com',
        'password': 'correct_password',
        }
    await add_user(**data)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    url = f'/api/v1/user/'
    response = await default_client_function.get(url, headers=headers)
    content = response.json()

    assert response.status_code == 200
    assert {'username': 'tokenuser@mail.com'} in response.json()

@pytest.mark.asyncio(loop_scope='session')
async def test_retrieve_all_users_wrong_token(
        default_client_function: httpx.AsyncClient,
        wrong_token: str,
    ) -> None:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {wrong_token}',
    }
    test_response = {
        'detail': 'Operation not allowed',
    }

    url = f'/api/v1/user/'
    response = await default_client_function.get(url, headers=headers)
    content = response.json()

    assert response.status_code == 403
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_retrieve_all_users_expired_token(
        default_client_function: httpx.AsyncClient,
        expired_token: str,
    ) -> None:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {expired_token}',
    }
    test_response = {
        'detail': 'Token expired',
    }

    url = f'/api/v1/user/'
    response = await default_client_function.get(url, headers=headers)
    content = response.json()

    assert response.status_code == 401
    assert response.json() == test_response

@pytest.mark.asyncio(loop_scope='session')
async def test_retrieve_all_users_invalid_token(
        default_client_function: httpx.AsyncClient,
        expired_token: str,
    ) -> None:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer invalid_token',
    }
    test_response = {
        'detail': 'Could not validate credentials',
    }

    url = f'/api/v1/user/'
    response = await default_client_function.get(url, headers=headers)
    content = response.json()

    assert response.status_code == 401
    assert response.json() == test_response
