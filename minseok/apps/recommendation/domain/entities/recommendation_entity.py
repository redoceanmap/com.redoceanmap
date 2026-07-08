from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Recommendation:
    """저장된 상권 추천 한 건 — ORM/프레임워크에 의존하지 않는 도메인 엔티티."""

    id: int
    conversation_id: int | None  # 이 추천을 만든 chat 대화(느슨한 참조, FK 없음)
    trdar_code: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    lat: float
    lng: float
    created_at: datetime
