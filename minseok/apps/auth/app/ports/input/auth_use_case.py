from abc import ABC, abstractmethod

from auth.app.dtos.token_dto import TokenDto
from auth.domain.entities.user_entity import User


class AuthUseCase(ABC):

    @abstractmethod
    async def register(
        self,
        email: str,
        password: str,
        name: str,
        terms_agreed: bool = True,
        marketing_agreed: bool = False,
    ) -> TokenDto: ...

    @abstractmethod
    async def login(self, email: str, password: str) -> TokenDto: ...

    @abstractmethod
    async def refresh(self, refresh_token: str) -> TokenDto: ...

    @abstractmethod
    async def get_me(self, token: str) -> User | None: ...
