"""BFF 인증 쿠키 조립 — 속성 나열은 이 파일 한 곳만 (bff-cloudflared-harness 규칙 2·B.2).

스펙 고정: HttpOnly + SameSite=Lax + Path=/ (리터럴). Secure는 prod에서만,
Domain은 env COOKIE_DOMAIN(prod `.redoceanmap.com`, dev 미설정=host-only) — 이 둘만 ENV 분기.
state·consent 쿠키는 10분 단기(호스트 전용 — auth 오리진에서만 쓰인다).
"""
from __future__ import annotations

from fastapi import Response

from core.config import COOKIE_DOMAIN, ENV

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
STATE_COOKIE = "oauth_state"
RETURN_TO_COOKIE = "oauth_return_to"
CONSENT_COOKIE = "consent_token"

ACCESS_MAX_AGE = 60 * 60           # auth_interactor.ACCESS_TOKEN_EXPIRE_MINUTES와 일치
REFRESH_MAX_AGE = 14 * 24 * 3600   # REFRESH_TOKEN_EXPIRE_DAYS와 일치
SHORT_MAX_AGE = 10 * 60            # state·consent — 로그인 절차 안에서만 유효

_SECURE = ENV == "production"
_DOMAIN = COOKIE_DOMAIN or None


def _set(response: Response, key: str, value: str, max_age: int, domain: str | None) -> None:
    response.set_cookie(
        key=key, value=value, max_age=max_age,
        httponly=True, samesite="lax", secure=_SECURE, path="/", domain=domain,
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    _set(response, ACCESS_COOKIE, access_token, ACCESS_MAX_AGE, _DOMAIN)
    _set(response, REFRESH_COOKIE, refresh_token, REFRESH_MAX_AGE, _DOMAIN)


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/", domain=_DOMAIN)
    response.delete_cookie(REFRESH_COOKIE, path="/", domain=_DOMAIN)


def set_oauth_state_cookies(response: Response, state: str, return_to: str) -> None:
    # 호스트 전용(도메인 미지정) — start와 callback이 같은 오리진(auth)이라 공유 불필요
    _set(response, STATE_COOKIE, state, SHORT_MAX_AGE, None)
    _set(response, RETURN_TO_COOKIE, return_to, SHORT_MAX_AGE, None)


def clear_oauth_state_cookies(response: Response) -> None:
    response.delete_cookie(STATE_COOKIE, path="/")
    response.delete_cookie(RETURN_TO_COOKIE, path="/")


def set_consent_cookie(response: Response, consent_token: str) -> None:
    _set(response, CONSENT_COOKIE, consent_token, SHORT_MAX_AGE, None)


def clear_consent_cookie(response: Response) -> None:
    response.delete_cookie(CONSENT_COOKIE, path="/")
