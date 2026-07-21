from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.area_dto import AreaListResponse


class AreaUseCase(ABC):
    """어드민 상권 목록 유스케이스 — 전 상권의 최신 분기 집계."""

    @abstractmethod
    async def list_areas(self) -> AreaListResponse:
        """전 상권의 점포수·폐업률·월매출 집계를 반환한다(필터는 프론트 몫)."""
        ...
