from abc import ABC, abstractmethod

from auth.app.dtos.social_dto import SocialLoginResultDto, SocialProfileDto
from auth.app.dtos.token_dto import TokenDto


class SocialUseCase(ABC):

    @abstractmethod
    async def login(self, provider: str, code: str, redirect_uri: str) -> SocialLoginResultDto: ...

    @abstractmethod
    async def complete_consent(self, consent_token: str, marketing_agreed: bool) -> TokenDto: ...

    @abstractmethod
    def peek_consent(self, consent_token: str) -> SocialProfileDto:
        """동의 대기 토큰의 프로필 열람(검증 포함) — 동의 페이지 표시용. 무효면 ValueError."""
        ...
