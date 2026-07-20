import pytest

from auth.app.dtos.social_dto import SocialProfileDto
from auth.app.use_cases.social_interactor import SocialInteractor
from auth.domain.entities.refresh_token_entity import RefreshToken
from auth.domain.entities.user_entity import User


class _StubProfilePort:
    def __init__(self, profile: SocialProfileDto | None = None):
        self.profile = profile

    async def fetch_profile(self, provider, code, redirect_uri):
        if self.profile is None:
            raise ValueError("소셜 로그인 인증에 실패했습니다. 다시 시도해 주세요.")
        return self.profile


class _StubUserRepository:
    def __init__(self):
        self.users: dict[int, User] = {}
        self._seq = 0

    async def find_by_email(self, email):
        return next((u for u in self.users.values() if u.email == email), None)

    async def find_by_id(self, user_id):
        return self.users.get(user_id)

    async def create(self, email, password_hash, name):
        self._seq += 1
        user = User(id=self._seq, email=email, password_hash=password_hash, name=name)
        self.users[user.id] = user
        return user


class _StubRefreshTokenRepository:
    def __init__(self):
        self.tokens: dict[str, RefreshToken] = {}

    async def create(self, user_id, token, expires_at):
        entity = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.tokens[token] = entity
        return entity

    async def find_by_token(self, token):
        return self.tokens.get(token)

    async def delete(self, token):
        self.tokens.pop(token, None)


def _interactor(profile: SocialProfileDto | None):
    return SocialInteractor(
        profile_port=_StubProfilePort(profile),
        repository=_StubUserRepository(),
        refresh_repository=_StubRefreshTokenRepository(),
    )


async def test_신규_이메일이면_계정을_만들고_토큰_쌍을_발급한다():
    interactor = _interactor(SocialProfileDto(provider="google", email="a@b.c", name="장민석"))
    result = await interactor.login("google", "code", "http://localhost:3000/oauth/google")
    assert result.access_token
    assert result.refresh_token in interactor.refresh_repository.tokens
    assert result.email == "a@b.c"
    assert len(interactor.repository.users) == 1


async def test_기존_이메일이면_새_계정을_만들지_않고_그_계정으로_로그인한다():
    interactor = _interactor(SocialProfileDto(provider="kakao", email="a@b.c", name="카카오이름"))
    existing = await interactor.repository.create("a@b.c", "기존해시", "장민석")
    result = await interactor.login("kakao", "code", "http://localhost:3000/oauth/kakao")
    assert len(interactor.repository.users) == 1
    assert result.name == existing.name  # 기존 계정 유지 — 프로필 이름으로 덮지 않음


async def test_소셜_계정의_비밀번호_해시는_비어있지_않다():
    interactor = _interactor(SocialProfileDto(provider="naver", email="n@b.c", name="네이버"))
    await interactor.login("naver", "code", "http://localhost:3000/oauth/naver")
    user = await interactor.repository.find_by_email("n@b.c")
    assert user.password_hash  # 랜덤 해시 — 비밀번호 로그인 경로가 열리지 않는다


async def test_프로바이더_교환_실패는_ValueError로_전파된다():
    interactor = _interactor(profile=None)
    with pytest.raises(ValueError):
        await interactor.login("google", "잘못된코드", "http://localhost:3000/oauth/google")
