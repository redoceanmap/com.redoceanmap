from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    """사용자 도메인 엔티티 — ORM/프레임워크에 의존하지 않는다."""

    id: int
    email: str
    password_hash: str
    name: str
    terms_agreed_at: datetime | None = None  # 필수 약관 동의 시각 (구 유저는 None)
    marketing_agreed: bool = False
