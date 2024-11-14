from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession,
)
from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column,
)

from src.config import get_db_url


DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

str_pk = Annotated[str, mapped_column(primary_key=True)]
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(),
                                               onupdate=datetime.now)]
str_not_null = Annotated[str, mapped_column(nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class User(Base):
    __tablename__ = 'users'

    username: Mapped[str_pk]
    password: Mapped[str_not_null]
    telegram_id: Mapped[int] = mapped_column(nullable=True)

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int_pk]
    sender: Mapped[str_not_null]
    recipient: Mapped[str_not_null]
    content: Mapped[str_not_null]
    read:  Mapped[bool] = mapped_column(default=False)

async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_session() -> AsyncSession:  # pragma: no cover
    return async_session_maker
