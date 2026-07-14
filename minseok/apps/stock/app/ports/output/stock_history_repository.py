from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_history_dto import StockNewsItem
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot
from stock.domain.entities.price_bar import PriceBar


class StockHistoryRepositoryPort(ABC):
    """수집 데이터 조회 아웃바운드 포트. 거래소 접미 매칭(005930 ↔ 005930.KS)은 구현이 맡는다."""

    @abstractmethod
    async def find_bars(self, symbol: str, timeframe: str, limit: int) -> list[PriceBar]:
        """최신 limit개 봉을 ts 오름차순으로 반환한다. 없으면 빈 목록."""
        ...

    @abstractmethod
    async def find_news(self, symbol: str, limit: int) -> list[StockNewsItem]:
        """뉴스+라벨을 발행일 내림차순으로 반환한다."""
        ...

    @abstractmethod
    async def find_latest_fundamentals(self, symbol: str) -> list[FundamentalSnapshot]:
        """소스(yfinance/dart)별 최신 스냅샷 각 1건을 반환한다."""
        ...
