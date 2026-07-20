import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

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

    async def login(self, provider: str, code: str, redirect_uri: str) -> TokenDto:
        profile = await self.profile_port.fetch_profile(provider, code, redirect_uri)
        # 이메일 기준 연동 — 같은 이메일이 있으면 기존 계정으로 로그인, 없으면 신규 생성.
        user = await self.repository.find_by_email(profile.email)
        if user is None:
            user = await self.repository.create(
                profile.email, self._unusable_password_hash(), profile.name
            )
        return await self._issue_tokens(user)
