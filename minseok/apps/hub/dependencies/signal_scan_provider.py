from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort
from hub.app.use_cases.signal_scan_interactor import SignalScanInteractor
from hub.dependencies.stock_analysis_provider import get_stock_analysis_port_batch


def get_signal_scan_use_case(
    stocks: StockAnalysisPort = Depends(get_stock_analysis_port_batch),
) -> SignalScanUseCase:
    # 배치 포트 — 크론 스캔이 사용자 질문 수요(stock_demand)를 오염시키지 않게 기록 없는 구현
    return SignalScanInteractor(stocks=stocks)
