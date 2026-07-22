from pydantic import BaseModel


class SocialConsentRequest(BaseModel):
    # 동의 토큰은 콜백이 심은 httpOnly 쿠키로만 전달된다(본문 금지 — BFF 규칙 2·3)
    marketing_agreed: bool = False  # 선택 — 마케팅 정보 수신 동의
