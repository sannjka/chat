from datetime import timedelta
import asyncio

import httpx
import pytest
import pytest_asyncio

from src.webapp.utils import get_users


@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_register_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/register/')
    assert response.status_code == 200
    assert 'Register to chat' in response.text
    assert '<form method="POST"' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_register_post_success(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        'password_check': 'new_password',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/'
    assert 'Log out' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_register_post_already_exists(
        default_client_function: httpx.AsyncClient,
        add_user,
    ) -> None:
    data = {
        'username': 'user_exists@mail.com',
        'password': 'password_exists',
        'password_check': 'password_exists',
        }
    await add_user(**data)
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'User with supplied username exists' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_register_post_email_validation_fail(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'wrong_username',
        'password': 'password',
        'password_check': 'password',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'Validation error' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_register_post_password_validation_fail(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'new_user@mail.com',
        'password': 'new_password',
        'password_check': 'wrong_confirmation',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'Validation error' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_login_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/login/')
    assert response.status_code == 200
    assert 'Login to chat' in response.text
    assert '<form method="POST"' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_login_post_success(
        default_client_function: httpx.AsyncClient,
        add_user,
    ) -> None:
    data = {
        'username': 'user_exists@mail.com',
        'password': 'correct_password',
        }
    await add_user(**data)
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/'
    assert 'Log out' in response.text
    assert 'Bearer' in default_client_function.cookies.get('access_token')

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_login_post_email_validation_fail(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'wrong',
        'password': 'password',
        }
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/login/'
    assert 'Validation error' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_login_post_wrong_user(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'wrong@mail.com',
        'password': 'password',
        }
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/login/'
    assert 'Incorrect Email or Password' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_login_post_wrong_password(
        default_client_function: httpx.AsyncClient,
        add_user,
    ) -> None:
    data = {
        'username': 'user_exists@mail.com',
        'password': 'correct_password',
        }
    await add_user(**data)
    data['password'] = 'wrong'
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/login/'
    assert 'Incorrect Email or Password' in response.text

@pytest.mark.asyncio(loop_scope='session')
async def test_webapp_logout_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/logout/',
                                                 follow_redirects=True)
    assert response.status_code == 200
    assert 'Not authorized' in response.text
    assert 'Log In' in response.text
    assert default_client_function.cookies.get('access_token') == None

@pytest.mark.asyncio(loop_scope='session')
async def test_get_users_in_login_route(
        client_for_get_users: httpx.AsyncClient,
        add_user,
    ) -> None:
    data1 = {
        'username': 'user1@mail.com',
        'password': 'password1',
        }
    data2 = {
        'username': 'user2@mail.com',
        'password': 'password2',
        }
    await asyncio.gather(*[add_user(**data) for data in [data1, data2]])

    response = await client_for_get_users.post(
        '/login/', follow_redirects=True, data=data1,
    )
    assert data2['username'] in response.text
