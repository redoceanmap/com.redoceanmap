from __future__ import annotations

import logging

from hub.app.dtos.stock_demand_dto import StockDemandRow
from hub.app.ports.input.stock_demand_use_case import StockDemandUseCase
from hub.app.ports.output.stock_demand_port import StockDemandPort

logger = logging.getLogger(__name__)


class StockDemandInteractor(StockDemandUseCase):
    """수요 조회 허브 대장 — 스포크(stock) 구현 포트에 위임한다."""

    def __init__(self, demand: StockDemandPort) -> None:
        self._demand = demand

    async def top_demands(self, days: int, limit: int) -> list[StockDemandRow]:
        rows = await self._demand.top_demands(days=days, limit=limit)
        logger.info("[hub-demand] 최근 %d일 수요 %d행 조회", days, len(rows))
        return rows
