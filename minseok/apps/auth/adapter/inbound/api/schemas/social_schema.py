from pydantic import BaseModel


class SocialLoginRequest(BaseModel):
    provider: str  # google | kakao | naver
    code: str  # OAuth 인가 코드
    redirect_uri: str  # 인가 요청에 사용한 것과 동일해야 교환 성공
