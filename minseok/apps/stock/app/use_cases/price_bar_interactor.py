from __future__ import annotations

import logging

from stock.app.dtos.price_bar_dto import PriceBarCoverage
from stock.app.ports.input.price_bar_use_case import PriceBarIngestUseCase
from stock.app.ports.output.price_bar_repository import PriceBarRepositoryPort
from stock.domain.entities.price_bar import PriceBar

logger = logging.getLogger(__name__)


class PriceBarInteractor(PriceBarIngestUseCase):
    """OHLCV 적재 대장. 저장(중복 무시)만 담당하고 해석은 분석 시점에 한다."""

    def __init__(self, bars: PriceBarRepositoryPort) -> None:
        self._bars = bars

    async def ingest(self, bars: list[PriceBar]) -> int:
        saved = await self._bars.save_many(bars)
        logger.info("[stock-price] 수신 %d봉 중 신규 %d봉 저장", len(bars), saved)
        return saved

    async def coverage(self) -> list[PriceBarCoverage]:
        return await self._bars.coverage()
