"""추천 기록 계약 DTO.

허브(hub)가 공개하는 앱 간 협력 계약의 일부. chat(생성 주체)이 채워서 넘기고
recommendation(영속 주체)이 소비한다. 저장 전 초안이라 id·created_at은 없다.
외부 의존 없는 순수 도메인 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendedArea:
    """기록할 추천 한 건(상권 1곳)."""

    trdar_code: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    lat: float
    lng: float
