from __future__ import annotations

from hub.app.dtos.price_bar_dto import PriceBarItem, PriceCoverageItem
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from stock.app.ports.input.price_bar_use_case import PriceBarIngestUseCase
from stock.domain.entities.price_bar import PriceBar


class PriceBarStorageGateway(PriceBarStoragePort):
    """허브 PriceBarStoragePort 구현 — 허브 계약 DTO를 도메인 엔티티로 변환해 유스케이스에 위임."""

    def __init__(self, use_case: PriceBarIngestUseCase) -> None:
        self._use_case = use_case

    async def save_many(self, items: list[PriceBarItem]) -> int:
        return await self._use_case.ingest([
            PriceBar(
                ticker=i.ticker, timeframe=i.timeframe, ts=i.ts,
                open=i.open, high=i.high, low=i.low, close=i.close, volume=i.volume,
            )
            for i in items
        ])

    async def coverage(self) -> list[PriceCoverageItem]:
        return [
            PriceCoverageItem(
                ticker=c.ticker, timeframe=c.timeframe,
                first_ts=c.first_ts, last_ts=c.last_ts, bars=c.bars,
            )
            for c in await self._use_case.coverage()
        ]
