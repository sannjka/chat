from datetime import timedelta

import httpx
import pytest
import pytest_asyncio


@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_register_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/register/')
    assert response.status_code == 200
    assert 'Register to chat' in response.text
    assert '<form method="POST">' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_register_post_success(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'fiona@mail.com',
        'password': 'green!',
        'password_check': 'green!',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/'
    assert 'Log out' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_register_post_already_exists(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'fiona@mail.com',
        'password': 'green!',
        'password_check': 'green!',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    # Переделать на фикстуру создания пользователя
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'User with supplied username exists' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_register_post_email_validation_fail(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'fiona',
        'password': 'green!',
        'password_check': 'green!',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'Validation error' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_register_post_password_validation_fail(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'fiona@mail.com',
        'password': 'green!',
        'password_check': 'wrong',
        }
    response = await default_client_function.post(
        '/register/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/register/'
    assert 'Validation error' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_login_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/login/')
    assert response.status_code == 200
    assert 'Login to chat' in response.text
    assert '<form method="POST">' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_login_post_success(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    # этот тест не должен был пройти, потому что в рамках
    # loop_scope='function' такой пользователь еще не создавался
    # доработаю, когда сделаю фикстуру для тестовой базы базы данных
    data = {
        'username': 'fiona@mail.com',
        'password': 'green!',
        }
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/'
    assert 'Log out' in response.text
    assert 'Bearer' in default_client_function.cookies.get('access_token')

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_login_post_wrong_user(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    data = {
        'username': 'wrong@mail.com',
        'password': 'green!',
        }
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/login/'
    assert 'Incorrect Email or Password' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_login_post_wrong_password(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    # этот тест не должен был пройти, потому что в рамках
    # loop_scope='function' такой пользователь еще не создавался
    # доработаю, когда сделаю фикстуру для тестовой базы базы данных
    data = {
        'username': 'fiona@mail.com',
        'password': 'wrong',
        }
    response = await default_client_function.post(
        '/login/', follow_redirects=True, data=data,
    )
    assert response.status_code == 200
    assert response.url == 'http://app/login/'
    assert 'Incorrect Email or Password' in response.text

@pytest.mark.asyncio(loop_scope='function')
async def test_webapp_logout_get(
        default_client_function: httpx.AsyncClient,
    ) -> None:
    response = await default_client_function.get('/logout/',
                                                 follow_redirects=True)
    assert response.status_code == 200
    assert 'Not authorized' in response.text
    assert 'Log In' in response.text
    assert default_client_function.cookies.get('access_token') == None
