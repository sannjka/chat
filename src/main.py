from typing import List, Dict

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.auth.authenticate import authenticate
from src.api.v1.base import api_router
from src.database.orm import init_db
from src.webapp.base import webapp_router
from src.webapp import exceptions as user_exceptions
from src.models.users import TokenResponse


app = FastAPI()

app.include_router(api_router, prefix='/api/v1')
app.include_router(webapp_router, prefix='')

app.mount('/static', StaticFiles(directory='src/static'), name='static')

user_exceptions.include_app(app)

