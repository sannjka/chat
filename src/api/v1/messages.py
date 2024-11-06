from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth.authenticate import authenticate
from src.database.orm import get_session
from src.models.messages import Message, MessageRead
from src.database.repository import MessageRepository


message_router = APIRouter()


@message_router.get('/{friend}', response_model=List[MessageRead])
async def retrieve_all_messages(
        friend: str,
        user: str = Depends(authenticate),
        session: async_sessionmaker[AsyncSession] = Depends(get_session),
    ) -> List[MessageRead]:
    message_database = MessageRepository(session)
    return await message_database.get_dialog(interlocutor1=user,
                                             interlocutor2=friend)

@message_router.post('/')
async def create_message(
        message: Message,
        user: str = Depends(authenticate),
        session: async_sessionmaker[AsyncSession] = Depends(get_session),
    ) -> dict:
    message_database = MessageRepository(session)
    await message_database.add(message)
    return {'message': 'Message created successfully'}
