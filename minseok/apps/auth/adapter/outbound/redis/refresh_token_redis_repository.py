import json
from datetime import datetime

from redis.asyncio import Redis

from auth.app.ports.output.refresh_token_repository import RefreshTokenRepository
from auth.domain.entities.refresh_token_entity import RefreshToken

_KEY_PREFIX = "auth:refresh:"


class RefreshTokenRedisRepository(RefreshTokenRepository):
    """리프레시 토큰을 Redis에 저장 — 만료 폐기는 키 TTL(EXPIREAT)에 위임한다."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        value = json.dumps({"user_id": user_id, "expires_at": expires_at.isoformat()})
        await self._redis.set(_KEY_PREFIX + token, value, exat=int(expires_at.timestamp()))
        return RefreshToken(user_id=user_id, token=token, expires_at=expires_at)

    async def find_by_token(self, token: str) -> RefreshToken | None:
        raw = await self._redis.get(_KEY_PREFIX + token)
        if raw is None:
            return None
        data = json.loads(raw)
        return RefreshToken(
            user_id=int(data["user_id"]),
            token=token,
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    async def delete(self, token: str) -> None:
        await self._redis.delete(_KEY_PREFIX + token)
