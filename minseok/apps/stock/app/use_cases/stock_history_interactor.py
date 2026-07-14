from __future__ import annotations

import logging

from stock.app.dtos.stock_history_dto import (
    FundamentalsQuery,
    FundamentalsView,
    PriceHistory,
    PriceHistoryQuery,
    StockNewsItem,
    StockNewsQuery,
)
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.input.stock_history_use_case import StockHistoryUseCase
from stock.app.ports.output.stock_history_repository import StockHistoryRepositoryPort

logger = logging.getLogger(__name__)


class StockHistoryInteractor(StockHistoryUseCase):
    """수집 데이터 조회 대장 — 심볼 정규화 후 저장소 조회를 조립한다.

    분석(StockInteractor·yfinance 라이브)과 달리 DB에 축적된 것만 읽는다.
    가격은 워치리스트 종목만 보유하므로 미보유 심볼은 명시적으로 404 계열 예외를 낸다.
    """

    def __init__(self, history: StockHistoryRepositoryPort) -> None:
        self._history = history

    async def price_history(self, query: PriceHistoryQuery) -> PriceHistory:
        symbol = _normalize(query.symbol)
        bars = await self._history.find_bars(symbol, query.timeframe, query.limit)
        if not bars:
            raise MarketDataUnavailableError(
                f"수집된 {query.timeframe} 봉이 없습니다(수집 대상 아님): {query.symbol}"
            )
        return PriceHistory(
            symbol=symbol,
            resolved_ticker=bars[0].ticker,
            timeframe=query.timeframe,
            bars=bars,
        )

    async def news(self, query: StockNewsQuery) -> list[StockNewsItem]:
        return await self._history.find_news(_normalize(query.symbol), query.limit)

    async def fundamentals(self, query: FundamentalsQuery) -> FundamentalsView:
        symbol = _normalize(query.symbol)
        snapshots = await self._history.find_latest_fundamentals(symbol)
        return FundamentalsView(symbol=symbol, snapshots=snapshots)


def _normalize(symbol: str) -> str:
    """티커 표기 통일 — DB 티커는 대문자(AAPL, 005930.KS)로 저장된다."""
    return symbol.strip().upper()
