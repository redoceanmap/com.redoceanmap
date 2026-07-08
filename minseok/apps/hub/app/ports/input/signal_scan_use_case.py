from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.stock_analysis_dto import StockAnalysisResult


class SignalScanUseCase(ABC):
    """관심 종목 목록을 일괄 분석하는 허브 유스케이스(자동화 알림용)."""

    @abstractmethod
    async def scan(self, symbols: list[str]) -> list[StockAnalysisResult]:
        """분석 결과 목록을 반환한다. 해석 실패 종목은 건너뛴다."""
        ...
