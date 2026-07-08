from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecommendationDraft:
    """추천 저장 요청 입력 — 추천 한 건(상권). 생성 주체(chat 등)가 채워 넘긴다."""

    trdar_code: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    lat: float
    lng: float
