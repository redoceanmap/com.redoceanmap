from datetime import datetime, timedelta, timezone

from auth.adapter.outbound.redis.refresh_token_redis_repository import (
    RefreshTokenRedisRepository,
)


class _FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}
        self.exat: dict[str, int] = {}

    async def set(self, key, value, exat=None):
        self.store[key] = value
        self.exat[key] = exat

    async def get(self, key):
        return self.store.get(key)

    async def delete(self, key):
        self.store.pop(key, None)


def _expires_at():
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=14)


async def test_저장하면_만료시각이_키_TTL로_설정된다():
    redis = _FakeRedis()
    repository = RefreshTokenRedisRepository(redis=redis)
    expires_at = _expires_at()
    created = await repository.create(user_id=1, token="tok", expires_at=expires_at)
    assert created.token == "tok"
    assert redis.exat["auth:refresh:tok"] == int(expires_at.timestamp())


async def test_저장한_토큰은_원형_그대로_조회된다():
    repository = RefreshTokenRedisRepository(redis=_FakeRedis())
    expires_at = _expires_at()
    await repository.create(user_id=7, token="tok", expires_at=expires_at)
    found = await repository.find_by_token("tok")
    assert found is not None
    assert found.user_id == 7
    assert found.expires_at == expires_at
    assert not found.is_expired()


async def test_없는_토큰은_None을_돌려준다():
    repository = RefreshTokenRedisRepository(redis=_FakeRedis())
    assert await repository.find_by_token("없는토큰") is None


async def test_삭제하면_더_이상_조회되지_않는다():
    repository = RefreshTokenRedisRepository(redis=_FakeRedis())
    await repository.create(user_id=1, token="tok", expires_at=_expires_at())
    await repository.delete("tok")
    assert await repository.find_by_token("tok") is None
