from typing import List, Dict

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory='src/templates')

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict[str, WebSocket]] = []

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append((client_id, websocket))

    def disconnect(self, client_id: str, websocket: WebSocket):
        self.active_connections.remove((client_id, websocket))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, client_id):
        for id, connection in self.active_connections:
            if id != client_id:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            personal_message = f'You say: {data}'
            common_message = f'Client #{client_id} says: {data}'
            await manager.send_personal_message(personal_message, websocket)
            await manager.broadcast(common_message, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id, websocket)
        left_message = f'Client #{client_id} left the chat'
        await manager.broadcast(left_message, client_id)

@app.get('/', response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})
