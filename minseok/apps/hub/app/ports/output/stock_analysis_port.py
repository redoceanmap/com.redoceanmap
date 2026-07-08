from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.stock_analysis_dto import StockAnalysisResult


class StockAnalysisUnavailable(Exception):
    """구현 스포크가 종목을 해석하거나 시세를 조회하지 못함 — 계약 수준 실패."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class StockAnalysisPort(ABC):
    """허브가 스포크에 위임하는 주식 분석 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크(stock)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def analyze(self, query: str) -> StockAnalysisResult:
        """종목명 또는 티커(자유 질의)를 해석해 분석한다.

        실패(미해석 종목·데이터 없음)는 StockAnalysisUnavailable로 알린다.
        """
        ...
