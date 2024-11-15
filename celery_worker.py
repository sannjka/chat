import asyncio

from celery import Celery
from aiogram import Bot
import asyncpg

from src.config import get_settings, get_db_url


settings = get_settings()
db_url = get_db_url().replace('+asyncpg', '')

worker = Celery(__name__, broker=settings.CELERY_BROKER)
worker.conf.broker_connection_retry_on_startup = True

async def send_notification(user: str, friend: str, message: str) -> None:
    chat_id = await get_chat_id(friend)
    if chat_id:
        bot = Bot(token=settings.TG_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)

async def get_chat_id(email: str) -> int | None:
    con = await asyncpg.connect(db_url)
    chat_id = await con.fetchval(
        'select telegram_id from users where username = $1',
        email,
    )
    await con.close()
    return chat_id

@worker.task(name='send_notification')
def notify(user, friend, message):
    asyncio.run(send_notification(user, friend, message))
    return f'from {user} to {friend}: {message}'
