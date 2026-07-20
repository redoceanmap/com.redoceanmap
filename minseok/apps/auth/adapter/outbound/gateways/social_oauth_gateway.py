import httpx

from auth.app.dtos.social_dto import SocialProfileDto
from auth.app.ports.output.social_profile_port import SocialProfilePort
from core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    KAKAO_CLIENT_ID,
    KAKAO_CLIENT_SECRET,
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET,
)


# 카카오싱크 콘솔(간편가입)에 이 태그명 그대로 등록해야 한다 — 자체 동의 화면과 동일 범위 강제.
KAKAO_REQUIRED_TAGS = {"age", "terms", "privacy"}  # 만 14세·이용약관·개인정보 수집
KAKAO_MARKETING_TAG = "marketing"


class SocialOauthGateway(SocialProfilePort):
    """인가 코드를 각 사 토큰 엔드포인트에서 교환하고 프로필 API로 이메일·이름을 가져온다."""

    async def fetch_profile(self, provider: str, code: str, redirect_uri: str) -> SocialProfileDto:
        if provider == "google":
            return await self._google(code, redirect_uri)
        if provider == "kakao":
            return await self._kakao(code, redirect_uri)
        if provider == "naver":
            return await self._naver(code, redirect_uri)
        raise ValueError(f"지원하지 않는 소셜 로그인입니다: {provider}")

    async def _exchange(self, client: httpx.AsyncClient, token_url: str, data: dict) -> str:
        res = await client.post(token_url, data=data)
        body = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
        access_token = body.get("access_token")
        if res.status_code != 200 or not access_token:
            raise ValueError("소셜 로그인 인증에 실패했습니다. 다시 시도해 주세요.")
        return access_token

    async def _google(self, code: str, redirect_uri: str) -> SocialProfileDto:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise ValueError("구글 로그인이 설정되지 않았습니다. (GOOGLE_CLIENT_ID/SECRET)")
        async with httpx.AsyncClient(timeout=10) as client:
            access_token = await self._exchange(
                client,
                "https://oauth2.googleapis.com/token",
                {
                    "grant_type": "authorization_code",
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            res = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        info = res.json()
        email = info.get("email")
        if res.status_code != 200 or not email:
            raise ValueError("구글 프로필 조회에 실패했습니다.")
        return SocialProfileDto(provider="google", email=email, name=info.get("name") or email.split("@")[0])

    async def _kakao(self, code: str, redirect_uri: str) -> SocialProfileDto:
        if not KAKAO_CLIENT_ID:
            raise ValueError("카카오 로그인이 설정되지 않았습니다. (KAKAO_CLIENT_ID)")
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        if KAKAO_CLIENT_SECRET:  # 카카오는 시크릿이 콘솔에서 선택 사항
            data["client_secret"] = KAKAO_CLIENT_SECRET
        async with httpx.AsyncClient(timeout=10) as client:
            access_token = await self._exchange(client, "https://kauth.kakao.com/oauth/token", data)
            res = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            terms_agreed, marketing_agreed = await self._kakao_service_terms(client, access_token)
        info = res.json() if res.status_code == 200 else {}
        account = info.get("kakao_account") or {}
        email = account.get("email")
        if not email:
            raise ValueError("카카오 계정의 이메일 제공 동의가 필요합니다.")
        nickname = (account.get("profile") or {}).get("nickname")
        return SocialProfileDto(
            provider="kakao",
            email=email,
            name=nickname or email.split("@")[0],
            provider_terms_agreed=terms_agreed,
            marketing_agreed=marketing_agreed,
        )

    async def _kakao_service_terms(
        self, client: httpx.AsyncClient, access_token: str
    ) -> tuple[bool, bool]:
        """카카오싱크 간편가입 동의 내역 조회 — (필수 약관 전부 동의, 마케팅 동의).

        자체 동의 화면과 동일한 범위(KAKAO_REQUIRED_TAGS 3종)가 전부 동의된 경우에만
        카카오 화면 동의로 인정한다 — 콘솔에 일부만 등록됐으면(예: 만14세 누락)
        자체 동의 페이지로 폴백해 동의 범위가 좁아지는 일을 막는다.
        미설정·조회 실패 시에도 (False, False) 폴백.
        """
        try:
            res = await client.get(
                "https://kapi.kakao.com/v2/user/service_terms",
                params={"result": "app_service_terms"},  # 앱에 등록된 전체 약관 + 동의 여부
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.HTTPError:
            return False, False
        if res.status_code != 200:
            return False, False
        return self._parse_kakao_terms(res.json().get("service_terms") or [])

    @staticmethod
    def _parse_kakao_terms(terms: list) -> tuple[bool, bool]:
        agreed_tags = {t.get("tag") for t in terms if t.get("agreed")}
        return KAKAO_REQUIRED_TAGS <= agreed_tags, KAKAO_MARKETING_TAG in agreed_tags

    async def _naver(self, code: str, redirect_uri: str) -> SocialProfileDto:
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            raise ValueError("네이버 로그인이 설정되지 않았습니다. (NAVER_CLIENT_ID/SECRET)")
        async with httpx.AsyncClient(timeout=10) as client:
            access_token = await self._exchange(
                client,
                "https://nid.naver.com/oauth2.0/token",
                {
                    "grant_type": "authorization_code",
                    "client_id": NAVER_CLIENT_ID,
                    "client_secret": NAVER_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            res = await client.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        info = (res.json() if res.status_code == 200 else {}).get("response") or {}
        email = info.get("email")
        if not email:
            raise ValueError("네이버 프로필 조회에 실패했습니다. (이메일 제공 동의 필요)")
        return SocialProfileDto(
            provider="naver", email=email, name=info.get("name") or info.get("nickname") or email.split("@")[0]
        )
