import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from auth.app.dtos.token_dto import TokenDto
from auth.domain.entities.user_entity import User
from auth.app.ports.input.auth_use_case import AuthUseCase
from auth.app.ports.output.user_repository import UserRepository

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class AuthInteractor(AuthUseCase):

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def _create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

    def _decode_token(self, token: str) -> int | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload["sub"])
        except JWTError:
            return None

    async def register(self, email: str, password: str, name: str) -> TokenDto:
        existing = await self.repository.find_by_email(email)
        if existing:
            raise ValueError("이미 사용 중인 이메일입니다.")
        user = await self.repository.create(email, self._hash_password(password), name)
        return TokenDto(access_token=self._create_token(user.id), name=user.name, email=user.email)

    async def login(self, email: str, password: str) -> TokenDto:
        user = await self.repository.find_by_email(email)
        if not user or not self._verify_password(password, user.password_hash):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        return TokenDto(access_token=self._create_token(user.id), name=user.name, email=user.email)

    async def get_me(self, token: str) -> User | None:
        user_id = self._decode_token(token)
        if user_id is None:
            return None
        return await self.repository.find_by_id(user_id)
