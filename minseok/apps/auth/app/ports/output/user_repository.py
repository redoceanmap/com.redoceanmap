from abc import ABC, abstractmethod

from auth.domain.entities.user_entity import User


class UserRepository(ABC):

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def create(self, email: str, password_hash: str, name: str) -> User: ...
