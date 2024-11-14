from typing import List, Dict, Tuple, Callable
import logging

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from httpx import AsyncClient

from .utils import get_httpx_client, api_create_message
from celery_worker import notify


logger = logging.getLogger('uvicorn.error')
chat_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict[Tuple(str), WebSocket]] = []

    async def connect(
            self, client_id: str, friend_id: str, websocket: WebSocket,
        ):
        await websocket.accept()
        self.active_connections.append(((client_id, friend_id), websocket))

    def disconnect(
            self, client_id: str, friend_id: str, websocket: WebSocket,
        ):
        self.active_connections.remove(((client_id, friend_id), websocket))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, client_id):
        for (cl_id, fr_id), connection in self.active_connections:
            if cl_id != client_id and fr_id == 'common':
                await self.send_personal_message(message, connection)

    async def send_private_message(self, message: str, client_id, friend_id):
        is_sent = False
        for (cl_id, fr_id), connection in self.active_connections:
            if cl_id == friend_id and fr_id == client_id:
                await self.send_personal_message(message, connection)
                is_sent = True
        if not is_sent:
            try:
                notify.delay(client_id, friend_id, message)
            except e:
                logger.debug(f'tg notification: {e}')

manager = ConnectionManager()


@chat_router.websocket('/ws/{client_id}/{friend_id}')
async def websocket_endpoint(
        websocket: WebSocket,
        client_id: str,
        friend_id: str,
        httpx_client: AsyncClient = Depends(get_httpx_client),
        save_message_to_db: Callable = Depends(api_create_message),
    ):
    await manager.connect(client_id, friend_id, websocket)
    try:
        async with httpx_client as client:
            while True:
                data = await websocket.receive_text()
                reverse_message = f'You say: {data}'
                forward_message = f'{client_id} says: {data}'
                await manager.send_personal_message(reverse_message, websocket)
                if friend_id == 'common':
                    await manager.broadcast(forward_message, client_id)
                else:
                    await manager.send_private_message(
                            forward_message, client_id, friend_id,
                    )
                    await save_message_to_db(message=data, client=client)
    except WebSocketDisconnect:
        manager.disconnect(client_id, friend_id, websocket)
        left_message = f'{client_id} left the chat'
        if friend_id == 'common':
            await manager.broadcast(left_message, client_id)
        else:
            await manager.send_private_message(
                    left_message, client_id, friend_id,
            )

