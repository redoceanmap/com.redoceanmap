from abc import ABC, abstractmethod

from auth.app.dtos.social_dto import SocialProfileDto


class SocialProfilePort(ABC):
    """인가 코드를 프로바이더(google·kakao·naver)에서 교환해 프로필을 가져오는 아웃바운드 포트."""

    @abstractmethod
    async def fetch_profile(self, provider: str, code: str, redirect_uri: str) -> SocialProfileDto: ...
