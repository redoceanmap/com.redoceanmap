from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.price_bar_dto import PriceBarCoverage
from stock.domain.entities.price_bar import PriceBar


class PriceBarRepositoryPort(ABC):
    """OHLCV 봉 저장/커버리지 조회 아웃바운드 포트. 구현(PG 등)은 어댑터가 제공."""

    @abstractmethod
    async def save_many(self, bars: list[PriceBar]) -> int:
        """저장하고 신규 건수를 반환한다. (ticker, timeframe, ts) 중복은 무시한다."""
        ...

    @abstractmethod
    async def coverage(self) -> list[PriceBarCoverage]:
        """(ticker, timeframe)별 보유 구간(min/max ts·봉 수)을 반환한다."""
        ...
