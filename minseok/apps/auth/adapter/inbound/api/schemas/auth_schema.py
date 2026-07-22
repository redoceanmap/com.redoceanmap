from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    terms_agreed: bool  # 필수 — 이용약관·개인정보 수집 동의 (false면 400)
    marketing_agreed: bool = False  # 선택 — 마케팅 정보 수신 동의


class LoginRequest(BaseModel):
    email: str
    password: str


class SessionResponse(BaseModel):
    """인증 성공 응답 — 토큰은 본문이 아니라 httpOnly Set-Cookie로만 내려간다(BFF 규칙 2)."""

    name: str
    email: str
