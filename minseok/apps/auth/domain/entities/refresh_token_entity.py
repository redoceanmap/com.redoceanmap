from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class RefreshToken:
    """리프레시 토큰 도메인 엔티티 — 회전(사용 즉시 폐기·재발급) 대상."""

    user_id: int
    token: str
    expires_at: datetime

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:  # DB가 naive로 돌려줘도 UTC 기준으로 비교
            expires = expires.replace(tzinfo=timezone.utc)
        return current >= expires
