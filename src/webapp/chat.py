from typing import List, Dict, Tuple

from fastapi import WebSocket, WebSocketDisconnect, APIRouter


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
        for (cl_id, fr_id), connection in self.active_connections:
            if cl_id == friend_id and fr_id == client_id:
                await self.send_personal_message(message, connection)

manager = ConnectionManager()


@chat_router.websocket('/ws/{client_id}/{friend_id}')
async def websocket_endpoint(
        websocket: WebSocket,
        client_id: str,
        friend_id: str,
    ):
    await manager.connect(client_id, friend_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            personal_message = f'You say: {data}'
            common_message = f'{client_id} says: {data}'
            await manager.send_personal_message(personal_message, websocket)
            if friend_id == 'common':
                await manager.broadcast(common_message, client_id)
            else:
                await manager.send_private_message(
                        common_message, client_id, friend_id,
                )
    except WebSocketDisconnect:
        manager.disconnect(client_id, friend_id, websocket)
        left_message = f'{client_id} left the chat'
        if friend_id == 'common':
            await manager.broadcast(left_message, client_id)
        else:
            await manager.send_private_message(
                    left_message, client_id, friend_id,
            )

