from dataclasses import dataclass

from auth.app.dtos.token_dto import TokenDto


@dataclass(frozen=True)
class SocialProfileDto:
    """OAuth 프로바이더에서 받아온 사용자 프로필.

    provider_terms_agreed: 프로바이더 동의 화면에 우리 서비스 약관이 포함되어
    (카카오싱크 간편가입 등) 필수 약관 동의까지 이미 끝난 경우 True — 자체 동의 페이지를 건너뛴다.
    """

    provider: str
    email: str
    name: str
    provider_terms_agreed: bool = False
    marketing_agreed: bool = False


@dataclass(frozen=True)
class SocialLoginResultDto:
    """소셜 로그인 결과 — 기존 유저면 토큰, 신규 유저면 약관 동의 요구.

    status == "ok"               → token 채워짐
    status == "consent_required" → consent_token·profile 채워짐 (아직 가입 안 됨)
    """

    status: str
    token: TokenDto | None = None
    consent_token: str | None = None
    profile: SocialProfileDto | None = None
