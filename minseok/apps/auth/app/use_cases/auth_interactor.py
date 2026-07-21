import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from auth.app.dtos.token_dto import TokenDto
from auth.domain.entities.user_entity import User
from auth.app.ports.input.auth_use_case import AuthUseCase
from auth.app.ports.output.refresh_token_repository import RefreshTokenRepository
from auth.app.ports.output.user_repository import UserRepository
from core.config import JWT_SECRET

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 짧게 — 갱신은 리프레시 토큰 회전으로
REFRESH_TOKEN_EXPIRE_DAYS = 14


class AuthInteractor(AuthUseCase):

    def __init__(self, repository: UserRepository, refresh_repository: RefreshTokenRepository) -> None:
        self.repository = repository
        self.refresh_repository = refresh_repository

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def _create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)

    def _decode_token(self, token: str) -> int | None:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            return int(payload["sub"])
        except JWTError:
            return None

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

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        terms_agreed: bool = True,
        marketing_agreed: bool = False,
    ) -> TokenDto:
        if not terms_agreed:
            raise ValueError("필수 약관에 동의해야 가입할 수 있습니다.")
        existing = await self.repository.find_by_email(email)
        if existing:
            raise ValueError("이미 사용 중인 이메일입니다.")
        user = await self.repository.create(
            email,
            self._hash_password(password),
            name,
            terms_agreed_at=datetime.now(timezone.utc),
            marketing_agreed=marketing_agreed,
        )
        return await self._issue_tokens(user)

    async def login(self, email: str, password: str) -> TokenDto:
        user = await self.repository.find_by_email(email)
        if not user or not self._verify_password(password, user.password_hash):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        user.ensure_active()  # 정지/탈퇴 계정 거부
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenDto:
        stored = await self.refresh_repository.find_by_token(refresh_token)
        if stored is None:
            raise ValueError("유효하지 않은 리프레시 토큰입니다.")
        await self.refresh_repository.delete(stored.token)  # 회전 — 재사용 차단
        if stored.is_expired():
            raise ValueError("리프레시 토큰이 만료되었습니다. 다시 로그인해 주세요.")
        user = await self.repository.find_by_id(stored.user_id)
        if user is None:
            raise ValueError("사용자를 찾을 수 없습니다.")
        user.ensure_active()  # 정지/탈퇴 계정은 재발급 거부
        return await self._issue_tokens(user)

    async def get_me(self, token: str) -> User | None:
        user_id = self._decode_token(token)
        if user_id is None:
            return None
        user = await self.repository.find_by_id(user_id)
        if user is None or user.deleted_at is not None or user.suspended_at is not None:
            return None  # 정지/탈퇴 계정은 세션 복원 차단 — 즉시 차단 정책과 일치
        return user
