from fastapi import APIRouter

from .users import user_router
from .messages import message_router


api_router = APIRouter(tags=['API'])
api_router.include_router(user_router, prefix='/user')
api_router.include_router(message_router, prefix='/message')
