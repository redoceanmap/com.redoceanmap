from datetime import datetime, timedelta, timezone

import pytest

from auth.app.use_cases.auth_interactor import AuthInteractor
from auth.domain.entities.refresh_token_entity import RefreshToken
from auth.domain.entities.user_entity import User


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


def _interactor():
    return AuthInteractor(
        repository=_StubUserRepository(),
        refresh_repository=_StubRefreshTokenRepository(),
    )


async def test_가입은_액세스와_리프레시_토큰_쌍을_발급한다():
    interactor = _interactor()
    result = await interactor.register("a@b.c", "pw1234", "장민석")
    assert result.access_token
    assert result.refresh_token
    assert result.email == "a@b.c"
    assert result.refresh_token in interactor.refresh_repository.tokens


async def test_가입은_필수_약관_동의_시각을_기록한다():
    interactor = _interactor()
    await interactor.register("a@b.c", "pw1234", "장민석", terms_agreed=True, marketing_agreed=True)
    user = await interactor.repository.find_by_email("a@b.c")
    assert user.terms_agreed_at is not None
    assert user.marketing_agreed is True


async def test_필수_약관_미동의_가입은_거부된다():
    interactor = _interactor()
    with pytest.raises(ValueError):
        await interactor.register("a@b.c", "pw1234", "장민석", terms_agreed=False)


async def test_중복_이메일_가입은_거부된다():
    interactor = _interactor()
    await interactor.register("a@b.c", "pw1234", "장민석")
    with pytest.raises(ValueError):
        await interactor.register("a@b.c", "pw5678", "다른사람")


async def test_로그인은_비밀번호가_틀리면_거부된다():
    interactor = _interactor()
    await interactor.register("a@b.c", "pw1234", "장민석")
    with pytest.raises(ValueError):
        await interactor.login("a@b.c", "틀린비번")
    result = await interactor.login("a@b.c", "pw1234")
    assert result.access_token


async def test_리프레시는_회전한다_사용한_토큰은_재사용_불가():
    interactor = _interactor()
    first = await interactor.register("a@b.c", "pw1234", "장민석")
    renewed = await interactor.refresh(first.refresh_token)
    assert renewed.refresh_token != first.refresh_token
    with pytest.raises(ValueError):  # 이미 회전(폐기)된 토큰
        await interactor.refresh(first.refresh_token)


async def test_만료된_리프레시_토큰은_거부되고_폐기된다():
    interactor = _interactor()
    result = await interactor.register("a@b.c", "pw1234", "장민석")
    expired = RefreshToken(
        user_id=1,
        token=result.refresh_token,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    interactor.refresh_repository.tokens[result.refresh_token] = expired
    with pytest.raises(ValueError):
        await interactor.refresh(result.refresh_token)
    assert result.refresh_token not in interactor.refresh_repository.tokens


async def test_알_수_없는_리프레시_토큰은_거부된다():
    interactor = _interactor()
    with pytest.raises(ValueError):
        await interactor.refresh("없는토큰")
