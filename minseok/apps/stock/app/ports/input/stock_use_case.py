from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.domain.value_objects.market_values import Symbol


class StockUseCase(ABC):

    @abstractmethod
    async def analyze(self, symbol: Symbol, name: str | None = None) -> StockAnalysis:
        """종목의 지표·뉴스를 결합해 방향 전망을 분석한다(매매 추천 아님).

        name은 수집 뉴스(DB) 검색용 이름(예: "삼성전자"). 없으면 코드로 검색한다.
        """
        ...
