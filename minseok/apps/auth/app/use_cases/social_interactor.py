import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from auth.app.dtos.social_dto import SocialLoginResultDto, SocialProfileDto
from auth.app.dtos.token_dto import TokenDto
from auth.app.ports.input.social_use_case import SocialUseCase
from auth.app.ports.output.refresh_token_repository import RefreshTokenRepository
from auth.app.ports.output.social_profile_port import SocialProfilePort
from auth.app.ports.output.user_repository import UserRepository
from auth.app.use_cases.auth_interactor import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from auth.domain.entities.user_entity import User
from core.config import JWT_SECRET

# 동의 대기 토큰 수명 — 동의 화면에서 머무는 시간만 버티면 된다.
CONSENT_TOKEN_EXPIRE_MINUTES = 10


class SocialInteractor(SocialUseCase):

    def __init__(
        self,
        profile_port: SocialProfilePort,
        repository: UserRepository,
        refresh_repository: RefreshTokenRepository,
    ) -> None:
        self.profile_port = profile_port
        self.repository = repository
        self.refresh_repository = refresh_repository

    def _unusable_password_hash(self) -> str:
        # 소셜 계정은 비밀번호 로그인 불가 — 아무도 모르는 랜덤 값을 해시해 저장한다.
        return bcrypt.hashpw(secrets.token_urlsafe(32).encode(), bcrypt.gensalt()).decode()

    def _create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)

    def _create_consent_token(self, profile: SocialProfileDto) -> str:
        # 유저 생성 전 프로필을 서명해 보관 — DB·Redis 없이 동의 완료 API에서 복원한다.
        expire = datetime.now(timezone.utc) + timedelta(minutes=CONSENT_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(
            {
                "purpose": "social_consent",
                "provider": profile.provider,
                "email": profile.email,
                "name": profile.name,
                "exp": expire,
            },
            JWT_SECRET,
            algorithm=ALGORITHM,
        )

    def _decode_consent_token(self, token: str) -> SocialProfileDto:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        except JWTError:
            raise ValueError("동의 절차가 만료되었습니다. 다시 로그인해 주세요.")
        if payload.get("purpose") != "social_consent":  # 액세스 토큰 등 다른 JWT 재사용 차단
            raise ValueError("잘못된 동의 요청입니다. 다시 로그인해 주세요.")
        return SocialProfileDto(
            provider=payload["provider"], email=payload["email"], name=payload["name"]
        )

    async def _issue_tokens(self, user: User) -> TokenDto:
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh = await self.refresh_repository.create(
            user_id=user.id, token=secrets.token_urlsafe(48), expires_at=expires_at
        )
        return TokenDto(
            access_token=self._create_token(user.id),
            refresh_token=refresh.token,
            name=user.name,
            email=user.email,
        )

    async def login(self, provider: str, code: str, redirect_uri: str) -> SocialLoginResultDto:
        profile = await self.profile_port.fetch_profile(provider, code, redirect_uri)
        # 이메일 기준 연동 — 같은 이메일이 있으면 기존 계정으로 로그인.
        user = await self.repository.find_by_email(profile.email)
        if user is None:
            if profile.provider_terms_agreed:
                # 카카오싱크 등 프로바이더 동의 화면에서 필수 약관까지 마친 경우 — 즉시 가입.
                user = await self.repository.create(
                    profile.email,
                    self._unusable_password_hash(),
                    profile.name,
                    terms_agreed_at=datetime.now(timezone.utc),
                    marketing_agreed=profile.marketing_agreed,
                )
                return SocialLoginResultDto(status="ok", token=await self._issue_tokens(user))
            # 그 외 신규 유저는 약관 동의 전까지 만들지 않는다 — 동의 대기 토큰만 발급.
            return SocialLoginResultDto(
                status="consent_required",
                consent_token=self._create_consent_token(profile),
                profile=profile,
            )
        return SocialLoginResultDto(status="ok", token=await self._issue_tokens(user))

    async def complete_consent(self, consent_token: str, marketing_agreed: bool) -> TokenDto:
        profile = self._decode_consent_token(consent_token)
        user = await self.repository.find_by_email(profile.email)
        if user is None:
            user = await self.repository.create(
                profile.email,
                self._unusable_password_hash(),
                profile.name,
                terms_agreed_at=datetime.now(timezone.utc),
                marketing_agreed=marketing_agreed,
            )
        return await self._issue_tokens(user)
