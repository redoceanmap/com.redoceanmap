from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.recommendation_log_dto import RecommendationLogQuery, RecommendationLogResponse


class RecommendationLogUseCase(ABC):
    """어드민 추천 기록 유스케이스 — 최근 추천 목록 + 총계/오늘 KPI."""

    @abstractmethod
    async def list_logs(self, query: RecommendationLogQuery) -> RecommendationLogResponse:
        """최근 추천 기록과 총계·오늘 건수를 반환한다."""
        ...
