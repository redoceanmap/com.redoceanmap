from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.area_detail_dto import AreaDetailQuery, AreaDetailView


class AreaDetailUseCase(ABC):
    """상권 1곳의 최신 분기 구조 분해 + 해석 문장 조회 — 프론트 지도 오버레이용."""

    @abstractmethod
    async def get_detail(self, query: AreaDetailQuery) -> AreaDetailView | None:
        """상권이 없으면 None(HTTP 변환은 라우터 몫)."""
        ...
