from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.market_values import Price, Symbol


class MarketDataPort(ABC):
    """시세·지표·뉴스 조회 아웃바운드 포트. 구현(시세 벤더 API 등)은 어댑터가 제공."""

    @abstractmethod
    async def latest_price(self, symbol: Symbol) -> Price: ...

    @abstractmethod
    async def indicators(self, symbol: Symbol) -> Indicators: ...

    @abstractmethod
    async def recent_headlines(self, symbol: Symbol) -> list[str]: ...
