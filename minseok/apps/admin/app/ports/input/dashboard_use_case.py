from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.dashboard_dto import DashboardResponse


class DashboardUseCase(ABC):
    """어드민 대시보드 유스케이스 — 회원·상권·추천 KPI 합성."""

    @abstractmethod
    async def summary(self) -> DashboardResponse:
        """회원 통계 + 상권 수·최신 분기 + 추천 추이/분포/최근 기록을 한 번에 반환한다."""
        ...
