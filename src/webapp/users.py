from typing import Annotated, Callable
from fastapi import (Request, APIRouter, Form, HTTPException, Cookie, status,
                     Depends)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from src.api.v1.users import sign_user_in, sign_new_user
from src.auth.authenticate import get_user_from_cookie
from src.models.users import User
from .forms import UserData, UserRegister


user_router = APIRouter()
templates = Jinja2Templates(directory='src/templates')


@user_router.get('/', response_class=HTMLResponse)
async def chat_interface(
        request: Request,
        user: str = Depends(get_user_from_cookie),
    ):
    return templates.TemplateResponse(
        request=request, name='chat.html', context={'user': user},
    )

@user_router.get('/register/', response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        request=request, name='register.html',
    )

@user_router.post('/register/', response_class=RedirectResponse)
async def register(request: Request, data: Annotated[UserRegister, Form()]):
    response = RedirectResponse(url='/')
    response.status_code = status.HTTP_303_SEE_OTHER
    try:
        await sign_new_user(user=User(**data.model_dump()))
    except HTTPException as exc:
        return templates.TemplateResponse(
            request=request, name='register.html',
            context={'user': None, 'msg': exc.detail},
        )
    else:
        await sign_user_in(response=response, form_data=data)
        return response

@user_router.get('/login/', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name='login.html')

@user_router.post('/login/', response_class=RedirectResponse)
async def login(request: Request, data: Annotated[UserData, Form()]):
    response = RedirectResponse(url='/')
    response.status_code = status.HTTP_303_SEE_OTHER
    try:
        await sign_user_in(response=response, form_data=data)
    except HTTPException:
        return templates.TemplateResponse(
            request=request, name='login.html',
            context={'msg': 'Incorrect Email or Password'},
        )
    else:
        return response

@user_router.get('/logout/', response_class=RedirectResponse)
async def logout(request: Request):
    response = RedirectResponse(url='/')
    response.delete_cookie('access_token')
    return response
