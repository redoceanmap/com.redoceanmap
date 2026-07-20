from pydantic import BaseModel


class SocialLoginRequest(BaseModel):
    provider: str  # google | kakao | naver
    code: str  # OAuth 인가 코드
    redirect_uri: str  # 인가 요청에 사용한 것과 동일해야 교환 성공


class SocialLoginResponse(BaseModel):
    """기존 유저면 토큰 4종, 신규 유저면 consent_token — status로 분기한다."""

    status: str  # ok | consent_required
    access_token: str | None = None
    refresh_token: str | None = None
    consent_token: str | None = None
    name: str | None = None
    email: str | None = None


class SocialConsentRequest(BaseModel):
    consent_token: str  # /social/login이 발급한 동의 대기 토큰
    marketing_agreed: bool = False  # 선택 — 마케팅 정보 수신 동의
