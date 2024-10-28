from typing import List, Dict

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth.authenticate import authenticate
from .users import user_router
from .chat import chat_router


webapp_router = APIRouter(tags=['WebApp'])
webapp_router.include_router(user_router, prefix='')
webapp_router.include_router(chat_router, prefix='')
