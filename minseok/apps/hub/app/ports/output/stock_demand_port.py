from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.stock_demand_dto import StockDemandRow


class StockDemandPort(ABC):
    """분석 질문 수요 조회 협력 — 수집 스크립트(소비)와 stock(구현·영속: stock_demand)을 잇는다."""

    @abstractmethod
    async def top_demands(self, days: int, limit: int) -> list[StockDemandRow]:
        """최근 days일 내 질문된 티커를 질문 수·최근성 순으로."""
        ...
