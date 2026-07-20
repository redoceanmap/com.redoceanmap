from dataclasses import dataclass


@dataclass(frozen=True)
class SocialProfileDto:
    """OAuth 프로바이더에서 받아온 사용자 프로필."""

    provider: str
    email: str
    name: str
