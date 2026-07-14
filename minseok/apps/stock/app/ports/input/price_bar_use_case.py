from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.price_bar_dto import PriceBarCoverage
from stock.domain.entities.price_bar import PriceBar


class PriceBarIngestUseCase(ABC):
    """수집기가 보낸 OHLCV 봉을 적재하는 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, bars: list[PriceBar]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...

    @abstractmethod
    async def coverage(self) -> list[PriceBarCoverage]:
        """(ticker, timeframe)별 보유 구간을 반환한다."""
        ...
