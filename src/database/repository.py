import abc
from typing import List

from pydantic import BaseModel

from src.models.users import User


class AbstractRepositoryUser(abc.ABC):

    @abc.abstractmethod
    async def add(self, user: User):
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, email: str) -> User:
        raise NotImplementedError

class FakeRepositoryUser(AbstractRepositoryUser):
    def __init__(self, users):
        self._users = list(users)

    async def add(self, user: User):
        self._users.append(user)

    async def get(self, email) -> User | None:
        try:
            return next(u for u in self._users if u.username == email)
        except StopIteration:
            return None

    async def list(self) -> List[User]:
        return list(self._users)

#class Database:
#    def __init__(self, model):
#        self.data = []
#
#    async def add(self, item: BaseModel) -> None:
#        seld.data.append(item)
#
#    async def get(self, id: int) -> Any:
#        for item in self.data:
#            if item.id == id:
#                return item
#        return None
#
#    async def list(self) -> List[Any]:
#        return list(self.data)
#
#    async def update(self, id: int, body: BaseModel) -> Any:
#        found = self.get(id)
#        if found:
#            body_data = body_model_dump()
#            for k, v in body_data.items():
#                if v is not None:
#                    found[k] = v
#            return found
#        return False
#
#    async def delete(self, id: PydanticObjectId) -> bool:
#        found = self.get(id)
#        if found:
#            self.data.remove(found)
