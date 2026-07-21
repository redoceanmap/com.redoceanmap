from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.entities.price_bar import PriceBar
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.market_values import Price, Symbol


class MarketDataPort(ABC):
    """시세·지표·뉴스 조회 아웃바운드 포트. 구현(시세 벤더 API 등)은 어댑터가 제공."""

    @abstractmethod
    async def latest_price(self, symbol: Symbol) -> Price: ...

    @abstractmethod
    async def quote(self, symbol: Symbol) -> Price:
        """현재가만 경량 조회 — 폴링용. latest_price(전체 이력 동반)와 달리 이력을 받지 않는다."""
        ...

    @abstractmethod
    async def indicators(self, symbol: Symbol) -> Indicators: ...

    @abstractmethod
    async def daily_bars(self, symbol: Symbol) -> list[PriceBar]:
        """일봉 이력(ts 오름차순, UTC) — 미수집 종목의 차트·예측 라이브 폴백용."""
        ...

    @abstractmethod
    async def recent_headlines(self, symbol: Symbol) -> list[str]: ...
