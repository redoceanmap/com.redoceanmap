from abc import ABC, abstractmethod

from auth.app.dtos.token_dto import TokenDto


class SocialUseCase(ABC):

    @abstractmethod
    async def login(self, provider: str, code: str, redirect_uri: str) -> TokenDto: ...
