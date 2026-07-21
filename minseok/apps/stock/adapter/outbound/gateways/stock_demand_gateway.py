from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hub.app.dtos.stock_demand_dto import StockDemandRow
from hub.app.ports.output.stock_demand_port import StockDemandPort
from stock.adapter.outbound.orm.stock_demand_orm import StockDemandOrm


class StockDemandGateway(StockDemandPort):
    """허브 StockDemandPort 구현 — stock_demand 테이블을 질문 수·최근성 순으로 조회한다."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def top_demands(self, days: int, limit: int) -> list[StockDemandRow]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        rows = (await self._session.execute(
            select(StockDemandOrm)
            .where(StockDemandOrm.last_asked_at >= cutoff)
            .order_by(StockDemandOrm.ask_count.desc(), StockDemandOrm.last_asked_at.desc())
            .limit(limit)
        )).scalars().all()
        return [
            StockDemandRow(ticker=r.ticker, ask_count=r.ask_count, last_asked_at=r.last_asked_at)
            for r in rows
        ]
