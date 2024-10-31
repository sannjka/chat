import abc
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.users import User
from src.database.orm import User as User_database


class Repository:
    model = None

    def __init__(self, session):
        self.session = session

    async def add(self, values):
        async with self.session() as session:
            async with session.begin():
                new_instance = self.model(**values.model_dump())
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
            return new_instance

    async def get(self, **filters):
        async with self.session() as session:
            query = select(self.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def list(self, **filters):
        async with self.session() as session:
            query = select(self.model)
            if filters:
                query = query.filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()

class UserRepository(Repository):
    model = User_database
