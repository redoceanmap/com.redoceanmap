from __future__ import annotations

import logging

from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort, StockAnalysisUnavailable

logger = logging.getLogger(__name__)


class SignalScanInteractor(SignalScanUseCase):
    """관심 종목 스캔 허브 대장 — 기존 StockAnalysisPort(스포크 구현)를 재사용한다.

    알림 여부 판단(방향 필터·발송)은 소비자(n8n 워크플로)의 몫이다.
    """

    def __init__(self, stocks: StockAnalysisPort) -> None:
        self._stocks = stocks

    async def scan(self, symbols: list[str]) -> list[StockAnalysisResult]:
        results: list[StockAnalysisResult] = []
        for symbol in symbols:
            try:
                results.append(await self._stocks.analyze(symbol))
            except StockAnalysisUnavailable as e:
                logger.warning("[hub-scan] %s 건너뜀: %s", symbol, e.detail)
        return results
