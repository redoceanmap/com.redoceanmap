from abc import ABC, abstractmethod

from auth.app.dtos.social_dto import SocialLoginResultDto
from auth.app.dtos.token_dto import TokenDto


class SocialUseCase(ABC):

    @abstractmethod
    async def login(self, provider: str, code: str, redirect_uri: str) -> SocialLoginResultDto: ...

    @abstractmethod
    async def complete_consent(self, consent_token: str, marketing_agreed: bool) -> TokenDto: ...
