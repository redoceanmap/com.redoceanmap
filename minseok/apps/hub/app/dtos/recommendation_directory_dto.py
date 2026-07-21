"""추천 기록 디렉토리 계약 DTO.

허브가 공개하는 앱 간 협력 계약의 일부. recommendation(스포크)이 채워서 반환하고
admin(스포크)이 소비한다. 원시 값만 담는 순수 도메인 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RecommendationInfo:
    id: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class MonthCount:
    month: str  # "YYYY-MM"
    count: int


@dataclass(frozen=True)
class CategoryCount:
    category: str
    count: int


@dataclass(frozen=True)
class RecommendationStats:
    total: int
    today: int
    monthly: list[MonthCount]  # 최근 12개월 오름차순
    top_categories: list[CategoryCount]  # 상위 업종 내림차순
