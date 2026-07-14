from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.area_stats_dto import AreaStatsQuery, AreaStatsView


class AreaStatsUseCase(ABC):
    """상권 1곳의 원시 수치 통계(분기 시계열 + 분해축) 조회 — 프론트 자료 패널용."""

    @abstractmethod
    async def get_stats(self, query: AreaStatsQuery) -> AreaStatsView | None:
        """상권이 없으면 None(HTTP 변환은 라우터 몫)."""
        ...
