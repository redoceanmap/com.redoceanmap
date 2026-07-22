from __future__ import annotations

import secrets
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse

from auth.adapter.inbound.api.cookie import (
    clear_consent_cookie,
    clear_oauth_state_cookies,
    set_auth_cookies,
    set_consent_cookie,
    set_oauth_state_cookies,
)
from auth.adapter.inbound.api.schemas.auth_schema import TokenResponse
from auth.adapter.inbound.api.schemas.social_schema import (
    SocialConsentRequest,
    SocialLoginRequest,
    SocialLoginResponse,
)
from auth.app.ports.input.social_use_case import SocialUseCase
from auth.dependencies.social_provider import get_social_use_case
from core.config import (
    AUTH_CALLBACK_BASE,
    GOOGLE_CLIENT_ID,
    KAKAO_CLIENT_ID,
    NAVER_CLIENT_ID,
)

social_router = APIRouter(prefix="/auth", tags=["auth"])

# 인가 URL 조립 재료 — 구 프론트 socialAuth.ts에서 서버로 이식(BFF: state·클라이언트 구성이
# 브라우저 JS 밖으로). prompt/auth_type: 프로바이더 세션 자동 통과 방지(기존 정책 유지).
_AUTHORIZE_URLS = {
    "google": "https://accounts.google.com/o/oauth2/v2/auth",
    "kakao": "https://kauth.kakao.com/oauth/authorize",
    "naver": "https://nid.naver.com/oauth2.0/authorize",
}
_EXTRA_PARAMS = {
    "google": {"scope": "openid email profile"},
    "kakao": {"prompt": "login"},
    "naver": {"auth_type": "reauthenticate"},
}


def _client_id(provider: str) -> str:
    ids = {"google": GOOGLE_CLIENT_ID, "kakao": KAKAO_CLIENT_ID, "naver": NAVER_CLIENT_ID}
    if provider not in ids:
        raise HTTPException(status_code=404, detail=f"지원하지 않는 프로바이더: {provider}")
    if not ids[provider]:
        raise HTTPException(status_code=503, detail=f"{provider} 로그인이 설정되지 않았습니다.")
    return ids[provider]


def _redirect_uri(provider: str) -> str:
    # redirect_uri는 서버가 조립(B.0) — 인가 요청과 코드 교환이 항상 같은 값을 쓴다
    return f"{AUTH_CALLBACK_BASE}/social/{provider}/callback"


def _front_base() -> str:
    """콜백 후 복귀할 프론트 오리진 — AUTH_CALLBACK_BASE에서 결정론적으로 유도.

    prod `https://auth.redoceanmap.com/auth` → auth. 접두를 뗀 apex.
    dev `http://localhost:3000/api/backend/auth` → 그 오리진 그대로.
    """
    u = urlparse(AUTH_CALLBACK_BASE)
    host = u.netloc[5:] if u.netloc.startswith("auth.") else u.netloc
    return f"{u.scheme}://{host}"


def _safe_return_to(return_to: str) -> str:
    # 오픈 리다이렉트 방지 — 사이트 내 경로만 허용("//host" 스킴 상대 URL도 거부)
    if return_to.startswith("/") and not return_to.startswith("//"):
        return return_to
    return "/"


@social_router.get("/social/{provider}/start")
async def social_start(provider: str, return_to: str = "/") -> RedirectResponse:
    """이중문 시작점(B.0) — 서버가 state 생성·쿠키 설정 후 프로바이더 인가 페이지로 302."""
    client_id = _client_id(provider)
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": client_id,
        "redirect_uri": _redirect_uri(provider),
        "response_type": "code",
        "state": state,
        **_EXTRA_PARAMS[provider],
    }
    response = RedirectResponse(
        f"{_AUTHORIZE_URLS[provider]}?{urlencode(params)}", status_code=302
    )
    set_oauth_state_cookies(response, state, _safe_return_to(return_to))
    return response


@social_router.get("/social/{provider}/callback")
async def social_callback(
    provider: str,
    code: str = "",
    state: str = "",
    oauth_state: str | None = Cookie(default=None),
    oauth_return_to: str | None = Cookie(default=None),
    use_case: SocialUseCase = Depends(get_social_use_case),
) -> RedirectResponse:
    """프로바이더 복귀 지점 — state 쿠키 검증 → 코드 교환(기존 인터랙터 재사용) → 쿠키 발급.

    브라우저 대상이라 실패도 JSON이 아니라 프론트로 302(?auth_error=) — 쿠키는 심지 않는다.
    """
    front = _front_base()
    _client_id(provider)  # 미지원 프로바이더는 404
    if not code or not state or oauth_state is None or state != oauth_state:
        response = RedirectResponse(f"{front}/?auth_error=state", status_code=302)
        clear_oauth_state_cookies(response)
        return response

    return_to = _safe_return_to(oauth_return_to or "/")
    try:
        result = await use_case.login(provider, code, _redirect_uri(provider))
    except ValueError:
        response = RedirectResponse(f"{front}/?auth_error=login", status_code=302)
        clear_oauth_state_cookies(response)
        return response

    if result.status == "consent_required":
        # 동의 대기 — 세션 쿠키는 심지 않고, 동의 토큰만 단기 httpOnly 쿠키로
        # (사용자 결정: URL 쿼리 금지 — 토큰이 히스토리·로그에 남지 않게).
        # 프론트 동의 페이지는 GET /auth/social/consent/pending으로 표시 정보를 읽는다.
        response = RedirectResponse(
            f"{front}/oauth/consent?{urlencode({'return_to': return_to})}", status_code=302
        )
        clear_oauth_state_cookies(response)
        set_consent_cookie(response, result.consent_token)
        return response

    response = RedirectResponse(f"{front}{return_to}", status_code=302)
    clear_oauth_state_cookies(response)
    set_auth_cookies(response, result.token.access_token, result.token.refresh_token)
    return response


@social_router.get("/social/consent/pending")
async def consent_pending(
    consent_token: str | None = Cookie(default=None),
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    """동의 페이지 표시 정보 — consent 쿠키의 프로필(이름·이메일). 쿠키 없거나 무효면 401."""
    if not consent_token:
        raise HTTPException(status_code=401, detail="동의 대기 상태가 아닙니다.")
    try:
        profile = use_case.peek_consent(consent_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"provider": profile.provider, "name": profile.name, "email": profile.email}


@social_router.post("/social/login", response_model=SocialLoginResponse)
async def social_login(
    body: SocialLoginRequest,
    response: Response,
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    """구(패턴 B) 코드 교환 — 프론트 전환(커밋 ④)까지 유지. 성공 시 쿠키도 함께 심는다."""
    try:
        result = await use_case.login(body.provider, body.code, body.redirect_uri)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if result.status == "consent_required":
        return SocialLoginResponse(
            status="consent_required",
            consent_token=result.consent_token,
            name=result.profile.name,
            email=result.profile.email,
        )
    set_auth_cookies(response, result.token.access_token, result.token.refresh_token)
    return SocialLoginResponse(
        status="ok",
        access_token=result.token.access_token,
        refresh_token=result.token.refresh_token,
        name=result.token.name,
        email=result.token.email,
    )


@social_router.post("/social/consent", response_model=TokenResponse)
async def social_consent(
    body: SocialConsentRequest,
    response: Response,
    consent_token: str | None = Cookie(default=None),
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    """동의 완료 — 본문 토큰(구 흐름) 우선, 없으면 쿠키(BFF 흐름). 성공 시 세션 쿠키 발급."""
    token = body.consent_token or consent_token
    if not token:
        raise HTTPException(status_code=401, detail="동의 토큰이 없습니다.")
    try:
        result = await use_case.complete_consent(token, body.marketing_agreed)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    set_auth_cookies(response, result.access_token, result.refresh_token)
    clear_consent_cookie(response)
    return result
