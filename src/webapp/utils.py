from typing import List

from fastapi import Request, Depends
from httpx import AsyncClient


async def get_httpx_client() -> AsyncClient:  # pragma: no cover
    return AsyncClient()

async def get_users(
        request: Request,
        httpx_client: AsyncClient = Depends(get_httpx_client),
        ) -> List:
    """ This function returns users only for logged in client
    """
    api_url = str(request.url)
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
            api_url+'api/v1/user/', headers=headers,
        )
    if users_response.status_code == 200:
        users = users_response.json()
        return users
    # we cannot be here if api route works
    return []  # pragma: no cover
