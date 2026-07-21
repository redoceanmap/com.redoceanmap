from __future__ import annotations

from admin.app.dtos.recommendation_log_dto import RecommendationLogQuery, RecommendationLogResponse
from admin.app.ports.input.recommendation_log_use_case import RecommendationLogUseCase
from hub.app.ports.output.recommendation_directory_port import RecommendationDirectoryPort

MAX_LIMIT = 200


class RecommendationLogInteractor(RecommendationLogUseCase):
    """어드민 추천 기록 대장 — 허브 RecommendationDirectoryPort에 위임한다."""

    def __init__(self, recommendations: RecommendationDirectoryPort) -> None:
        self._recommendations = recommendations

    async def list_logs(self, query: RecommendationLogQuery) -> RecommendationLogResponse:
        limit = min(max(query.limit, 1), MAX_LIMIT)
        stats = await self._recommendations.stats()
        items = await self._recommendations.list_recent(limit)
        return RecommendationLogResponse(total=stats.total, today=stats.today, items=items)
