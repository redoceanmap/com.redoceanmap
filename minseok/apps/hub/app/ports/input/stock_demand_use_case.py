from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.stock_demand_dto import StockDemandRow


class StockDemandUseCase(ABC):
    """수요 상위 조회 — 워치리스트 수요 편입 스크립트의 자동화 창구."""

    @abstractmethod
    async def top_demands(self, days: int, limit: int) -> list[StockDemandRow]: ...
