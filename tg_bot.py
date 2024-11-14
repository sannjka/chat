import asyncio
from contextlib import asynccontextmanager

import asyncpg
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from src.config import get_settings, get_db_url


settings = get_settings()
db_url = get_db_url().replace('+asyncpg', '')

bot = Bot(token=settings.TG_TOKEN)
dp = Dispatcher()


@asynccontextmanager
async def connect():
    con = await asyncpg.connect(db_url)
    yield con
    await con.close()

async def user_exists(con, email: str) -> bool:
    row = await con.fetchrow('select 1 from users where username = $1', email)
    return row is not None

async def update_id_in_db(con, tg_id: int, email: str) -> None:
    await con.execute('update users set telegram_id = $1 where username = $2',
                      tg_id, email)

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    await message.reply(
        'Бот для оповещения о пропущенных сообщений\n\n'
        'Чтобы подписаться отправьте адрес электронной '
        'почты, указанный при регистрации.',
        reply=False)

@dp.message(F.text.regexp(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$'))
async def subscribe(message: types.Message):
    async with connect() as con:
        if not await user_exists(con, message.text):
            answer_message = ('В приложении Chat не зарегистрирован '
                              'пользователь с таким email')
        else:
            await update_id_in_db(con, message.chat.id, message.text)
            answer_message = "Вы подписались"
    await message.reply(answer_message, reply=False)

@dp.message()
async def fail_reading_email(message: types.Message):
    answer_message = 'Не разобрал email'
    await message.reply(answer_message, reply=False)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
