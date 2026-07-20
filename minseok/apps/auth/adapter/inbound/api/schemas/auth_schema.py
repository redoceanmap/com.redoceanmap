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


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    name: str
    email: str
