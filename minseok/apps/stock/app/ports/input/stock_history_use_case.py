from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_history_dto import (
    FundamentalsQuery,
    FundamentalsView,
    PriceHistory,
    PriceHistoryQuery,
    StockNewsItem,
    StockNewsQuery,
)


class StockHistoryUseCase(ABC):
    """수집 데이터(OHLCV·뉴스·펀더멘털) 조회 인바운드 유스케이스 — 프론트 자료 패널용."""

    @abstractmethod
    async def price_history(self, query: PriceHistoryQuery) -> PriceHistory:
        """보유 봉을 ts 오름차순으로 반환한다. 봉이 없으면 MarketDataUnavailableError."""
        ...

    @abstractmethod
    async def news(self, query: StockNewsQuery) -> list[StockNewsItem]:
        """종목 뉴스를 발행일 내림차순으로 반환한다. 없으면 빈 목록."""
        ...

    @abstractmethod
    async def fundamentals(self, query: FundamentalsQuery) -> FundamentalsView:
        """소스별 최신 펀더멘털 스냅샷을 반환한다. 없으면 빈 snapshots."""
        ...
