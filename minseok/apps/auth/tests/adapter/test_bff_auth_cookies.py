"""BFF 전환(B.1~B.3) 라우터 계약 — start/callback·쿠키 발급·state 검증·logout.

스텁 유스케이스를 dependency_overrides로 주입해 어댑터(라우터) 계층만 검증한다.
쿠키 속성(HttpOnly·SameSite=Lax)은 Set-Cookie 헤더 원문으로 확인한다.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from auth.adapter.inbound.api.v1 import social_router as social_router_module
from auth.adapter.inbound.api.v1.auth_router import auth_router
from auth.adapter.inbound.api.v1.social_router import social_router
from auth.app.dtos.social_dto import SocialLoginResultDto, SocialProfileDto
from auth.app.dtos.token_dto import TokenDto
from auth.dependencies.auth_provider import get_auth_use_case
from auth.dependencies.social_provider import get_social_use_case

TOKENS = TokenDto(access_token="AT", refresh_token="RT", name="테스트", email="t@t.local")
PROFILE = SocialProfileDto(provider="google", email="new@t.local", name="신규")


class _StubSocial:
    def __init__(self, result: SocialLoginResultDto):
        self.result = result
        self.login_args = None
        self.consent_args = None

    async def login(self, provider, code, redirect_uri):
        self.login_args = (provider, code, redirect_uri)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    async def complete_consent(self, consent_token, marketing_agreed):
        self.consent_args = (consent_token, marketing_agreed)
        return TOKENS

    def peek_consent(self, consent_token):
        if consent_token != "CONSENT":
            raise ValueError("동의 절차가 만료되었습니다.")
        return PROFILE


class _StubAuth:
    def __init__(self):
        self.logged_out_with = "unset"

    async def login(self, email, password):
        return TOKENS

    async def register(self, email, password, name, terms_agreed, marketing_agreed):
        return TOKENS

    async def refresh(self, refresh_token):
        if refresh_token != "RT":
            raise ValueError("유효하지 않은 리프레시 토큰입니다.")
        return TOKENS

    async def logout(self, refresh_token):
        self.logged_out_with = refresh_token

    async def get_me(self, token):
        return None

    async def get_tabs(self, token):
        return ["market"]


def _client(social=None, auth=None) -> tuple[TestClient, _StubSocial, _StubAuth]:
    app = FastAPI()
    app.include_router(social_router)
    app.include_router(auth_router)
    social = social or _StubSocial(SocialLoginResultDto(status="ok", token=TOKENS))
    auth = auth or _StubAuth()
    app.dependency_overrides[get_social_use_case] = lambda: social
    app.dependency_overrides[get_auth_use_case] = lambda: auth
    return TestClient(app, follow_redirects=False), social, auth


@pytest.fixture(autouse=True)
def _fixed_client_ids(monkeypatch):
    for name in ("GOOGLE_CLIENT_ID", "KAKAO_CLIENT_ID", "NAVER_CLIENT_ID"):
        monkeypatch.setattr(social_router_module, name, "test-client-id")
    yield


def _set_cookie_headers(response) -> str:
    return "\n".join(response.headers.get_list("set-cookie"))


def test_start_redirects_with_state_cookie():
    client, _, _ = _client()
    res = client.get("/auth/social/google/start?return_to=/market")
    assert res.status_code == 302
    loc = res.headers["location"]
    assert loc.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=test-client-id" in loc
    assert "state=" in loc and "scope=openid+email+profile" in loc
    # redirect_uri는 서버(AUTH_CALLBACK_BASE)가 조립
    assert "%2Fsocial%2Fgoogle%2Fcallback" in loc
    cookies = _set_cookie_headers(res)
    assert "oauth_state=" in cookies
    assert "HttpOnly" in cookies
    assert "samesite=lax" in cookies.lower()
    assert 'oauth_return_to="/market"' in cookies or "oauth_return_to=/market" in cookies


def test_start_rejects_unknown_provider_and_external_return_to():
    client, _, _ = _client()
    assert client.get("/auth/social/github/start").status_code == 404
    res = client.get("/auth/social/kakao/start?return_to=https://evil.com/x")
    cookies = _set_cookie_headers(res)
    assert "evil.com" not in cookies  # 오픈 리다이렉트 방지 — "/"로 정규화


def test_callback_rejects_state_mismatch_without_cookies():
    client, _, _ = _client()
    client.cookies.set("oauth_state", "expected")
    res = client.get("/auth/social/google/callback?code=abc&state=tampered")
    assert res.status_code == 302
    assert "auth_error=state" in res.headers["location"]
    assert "access_token=" not in _set_cookie_headers(res).replace('access_token="";', "")


def test_callback_success_sets_httponly_cookies_and_returns_to_page():
    client, social, _ = _client()
    client.cookies.set("oauth_state", "S1")
    client.cookies.set("oauth_return_to", "/market")
    res = client.get("/auth/social/google/callback?code=abc&state=S1")
    assert res.status_code == 302
    assert res.headers["location"].endswith("/market")
    cookies = _set_cookie_headers(res)
    assert "access_token=AT" in cookies and "refresh_token=RT" in cookies
    assert cookies.count("HttpOnly") >= 2
    assert "samesite=lax" in cookies.lower()
    # 교환에 쓰인 redirect_uri도 서버 조립 값
    assert social.login_args[2].endswith("/social/google/callback")


def test_callback_consent_required_sets_consent_cookie_only():
    social = _StubSocial(SocialLoginResultDto(
        status="consent_required", consent_token="CONSENT", profile=PROFILE,
    ))
    client, _, _ = _client(social=social)
    client.cookies.set("oauth_state", "S1")
    res = client.get("/auth/social/google/callback?code=abc&state=S1")
    assert res.status_code == 302
    assert "/oauth/consent" in res.headers["location"]
    cookies = _set_cookie_headers(res)
    assert "consent_token=CONSENT" in cookies
    assert "access_token=AT" not in cookies  # 동의 전 세션 쿠키 금지


def test_consent_pending_reads_cookie():
    client, _, _ = _client()
    assert client.get("/auth/social/consent/pending").status_code == 401
    client.cookies.set("consent_token", "CONSENT")
    res = client.get("/auth/social/consent/pending")
    assert res.status_code == 200
    assert res.json()["email"] == "new@t.local"


def test_consent_post_uses_cookie_only():
    client, social, _ = _client()
    res = client.post("/auth/social/consent", json={"marketing_agreed": True})
    assert res.status_code == 401  # 쿠키 없으면 거부 — 본문 토큰 경로는 폐지됨
    client.cookies.set("consent_token", "CONSENT")
    res = client.post("/auth/social/consent", json={"marketing_agreed": True})
    assert res.status_code == 200
    assert social.consent_args == ("CONSENT", True)
    assert "access_token" not in res.json()  # 본문 토큰 0건
    assert "access_token=AT" in _set_cookie_headers(res)


def test_login_sets_cookies_and_body_has_no_tokens():
    client, _, _ = _client()
    res = client.post("/auth/login", json={"email": "t@t.local", "password": "pw"})
    assert res.status_code == 200
    body = res.json()
    assert body == {"name": "테스트", "email": "t@t.local"}  # 본문 토큰 0건(규칙 2)
    assert "access_token=AT" in _set_cookie_headers(res)


def test_refresh_accepts_cookie_only():
    client, _, _ = _client()
    client.cookies.set("refresh_token", "RT")
    res = client.post("/auth/refresh")
    assert res.status_code == 200
    assert "refresh_token=RT" in _set_cookie_headers(res)


def test_logout_revokes_and_clears_cookies():
    client, _, auth = _client()
    client.cookies.set("refresh_token", "RT")
    res = client.post("/auth/logout")
    assert res.status_code == 204
    assert auth.logged_out_with == "RT"
    cookies = _set_cookie_headers(res)
    assert 'access_token="";' in cookies and 'refresh_token="";' in cookies
