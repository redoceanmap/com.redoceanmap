from __future__ import annotations

import logging

from hub.app.dtos.price_bar_dto import PriceBarItem, PriceCoverageItem
from hub.app.ports.input.price_bar_ingest_use_case import PriceBarIngestUseCase
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort

logger = logging.getLogger(__name__)


class PriceBarIngestInteractor(PriceBarIngestUseCase):
    """OHLCV 수집 허브 대장 — 유효 봉만 골라 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: PriceBarStoragePort) -> None:
        self._storage = storage

    async def ingest(self, items: list[PriceBarItem]) -> int:
        valid = [i for i in items if i.ticker.strip() and i.high >= i.low > 0]
        if not valid:
            return 0
        saved = await self._storage.save_many(valid)
        logger.info("[hub-price] 수신 %d봉 중 신규 %d봉 저장", len(items), saved)
        return saved

    async def coverage(self) -> list[PriceCoverageItem]:
        return await self._storage.coverage()
