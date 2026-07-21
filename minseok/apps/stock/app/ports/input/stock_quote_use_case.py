from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_quote_dto import QuoteQuery, QuoteView


class StockQuoteUseCase(ABC):
    """현재가 경량 조회 — 프론트 30초 폴링용(차트 마지막 봉·헤더 가격 갱신)."""

    @abstractmethod
    async def quote(self, query: QuoteQuery) -> QuoteView:
        """시세 조회 실패는 MarketDataUnavailableError(HTTP 변환은 라우터 몫)."""
        ...
