from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.price_bar_dto import PriceBarItem, PriceCoverageItem


class PriceBarIngestUseCase(ABC):
    """자동화 수집기가 보낸 OHLCV 봉을 받아들이는 허브 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, items: list[PriceBarItem]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...

    @abstractmethod
    async def coverage(self) -> list[PriceCoverageItem]:
        """(ticker, timeframe)별 보유 구간을 반환한다."""
        ...
