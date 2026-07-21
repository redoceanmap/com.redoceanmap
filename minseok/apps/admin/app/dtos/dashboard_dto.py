from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.recommendation_directory_dto import (
    CategoryCount,
    MonthCount,
    RecommendationInfo,
)


@dataclass(frozen=True)
class DashboardResponse:
    member_total: int
    member_new_this_month: int
    area_count: int
    latest_quarter: str | None  # 예: "20251" — market 데이터 신선도 표시
    recommendation_total: int
    recommendation_today: int
    monthly: list[MonthCount]  # 최근 12개월 추천 추이
    top_categories: list[CategoryCount]
    recent: list[RecommendationInfo]  # 최근 추천 5건
