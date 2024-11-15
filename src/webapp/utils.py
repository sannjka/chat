from typing import List

from fastapi import Request, Depends, WebSocket
from httpx import AsyncClient

from celery_worker import notify


async def get_httpx_client() -> AsyncClient:
    return AsyncClient()

async def get_celery_notify():
    return notify

async def get_users(
        request: Request,
        httpx_client: AsyncClient = Depends(get_httpx_client),
        ) -> List:
    """ This function returns users only for logged in client
    """
    access_token = request.cookies.get('access_token')
    if not access_token:  # pragma: no cover
        # we are not supposed to be here
        return []

    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    async with httpx_client as client:
        users_response = await client.get(
            str(request.url_for('retrieve_all_users')), headers=headers,
        )
    if users_response.status_code == 200:
        users = users_response.json()
        return users
    # we cannot be here if api route works
    return []  # pragma: no cover

async def api_create_message(
        websocket: WebSocket,
        client_id: str,
        friend_id: str,
    ):
    async def _add_message_to_db(message, client):
        payload = {
            'sender': client_id,
            'recipient': friend_id,
            'content': message,
            }
        url = str(websocket.url_for('create_message'))
        access_token = websocket.cookies.get('access_token')
        if access_token:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': access_token,
            }
            message_response = await client.post(
                url, headers=headers, json=payload,
            )
    return _add_message_to_db
