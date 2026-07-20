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

    async def create(self, email, password_hash, name, terms_agreed_at=None, marketing_agreed=False):
        self._seq += 1
        user = User(
            id=self._seq,
            email=email,
            password_hash=password_hash,
            name=name,
            terms_agreed_at=terms_agreed_at,
            marketing_agreed=marketing_agreed,
        )
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


async def test_신규_이메일이면_가입시키지_않고_동의를_요구한다():
    interactor = _interactor(SocialProfileDto(provider="google", email="a@b.c", name="장민석"))
    result = await interactor.login("google", "code", "http://localhost:3000/oauth/google")
    assert result.status == "consent_required"
    assert result.consent_token
    assert result.profile.email == "a@b.c"
    assert len(interactor.repository.users) == 0  # 동의 전에는 유저를 만들지 않는다


async def test_동의를_완료하면_동의_시각과_함께_가입되고_토큰_쌍이_발급된다():
    interactor = _interactor(SocialProfileDto(provider="google", email="a@b.c", name="장민석"))
    pending = await interactor.login("google", "code", "http://localhost:3000/oauth/google")
    result = await interactor.complete_consent(pending.consent_token, marketing_agreed=True)
    assert result.access_token
    assert result.refresh_token in interactor.refresh_repository.tokens
    user = await interactor.repository.find_by_email("a@b.c")
    assert user.terms_agreed_at is not None
    assert user.marketing_agreed is True


async def test_카카오싱크로_필수_약관까지_동의한_신규_유저는_즉시_가입된다():
    interactor = _interactor(
        SocialProfileDto(
            provider="kakao",
            email="k@b.c",
            name="카카오",
            provider_terms_agreed=True,
            marketing_agreed=True,
        )
    )
    result = await interactor.login("kakao", "code", "http://localhost:3000/oauth/kakao")
    assert result.status == "ok"  # 자체 동의 페이지를 거치지 않는다
    assert result.token.access_token
    user = await interactor.repository.find_by_email("k@b.c")
    assert user.terms_agreed_at is not None
    assert user.marketing_agreed is True


async def test_프로바이더_동의가_없으면_카카오라도_자체_동의를_요구한다():
    # 콘솔에 간편가입 약관 미등록 등 — provider_terms_agreed=False 폴백
    interactor = _interactor(SocialProfileDto(provider="kakao", email="k@b.c", name="카카오"))
    result = await interactor.login("kakao", "code", "http://localhost:3000/oauth/kakao")
    assert result.status == "consent_required"
    assert len(interactor.repository.users) == 0


async def test_기존_이메일이면_동의_없이_그_계정으로_로그인한다():
    interactor = _interactor(SocialProfileDto(provider="kakao", email="a@b.c", name="카카오이름"))
    existing = await interactor.repository.create("a@b.c", "기존해시", "장민석")
    result = await interactor.login("kakao", "code", "http://localhost:3000/oauth/kakao")
    assert result.status == "ok"
    assert len(interactor.repository.users) == 1
    assert result.token.name == existing.name  # 기존 계정 유지 — 프로필 이름으로 덮지 않음


async def test_소셜_계정의_비밀번호_해시는_비어있지_않다():
    interactor = _interactor(SocialProfileDto(provider="naver", email="n@b.c", name="네이버"))
    pending = await interactor.login("naver", "code", "http://localhost:3000/oauth/naver")
    await interactor.complete_consent(pending.consent_token, marketing_agreed=False)
    user = await interactor.repository.find_by_email("n@b.c")
    assert user.password_hash  # 랜덤 해시 — 비밀번호 로그인 경로가 열리지 않는다


async def test_위조된_동의_토큰은_거부된다():
    interactor = _interactor(SocialProfileDto(provider="google", email="a@b.c", name="장민석"))
    with pytest.raises(ValueError):
        await interactor.complete_consent("위조토큰", marketing_agreed=False)


async def test_액세스_토큰을_동의_토큰으로_재사용할_수_없다():
    interactor = _interactor(SocialProfileDto(provider="google", email="a@b.c", name="장민석"))
    access_token = interactor._create_token(user_id=1)  # purpose 클레임 없음
    with pytest.raises(ValueError):
        await interactor.complete_consent(access_token, marketing_agreed=False)


async def test_프로바이더_교환_실패는_ValueError로_전파된다():
    interactor = _interactor(profile=None)
    with pytest.raises(ValueError):
        await interactor.login("google", "잘못된코드", "http://localhost:3000/oauth/google")
